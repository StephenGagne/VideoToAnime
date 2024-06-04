import os
import websocket
import uuid
import json
import urllib.request
import urllib.parse
from re import split
from shutil import copy
from shutil import move

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

##
# Function to generate images
# enteredPrompt:            A prompt used to style each image
# enteredNegativePrompt     A prompt used to excluded certain data from each image
##

def ai_generate(enteredPrompt, enteredNegativePrompt):
    #Split frames to use as input
    inputDir = "C:\\VideoToAnime\\originalFrames\\"
    comfyInputDir = "C:\\ComfyUI_windows_portable\\ComfyUI\\input\\"
    
    #Generated frames using Stable Diffusion
    comfyOutputDir = "C:\\ComfyUI_windows_portable\\ComfyUI\\output\\"
    outputDir = "C:\\VideoToAnime\\generatedFrames\\"
    
    #Stable Diffusion Settings
    modelName = "drippyWatercolor_jwlWatercolorDrippy.ckpt"
    # Samplers: dpmpp_sde, ddim
    sampler = "dpmpp_sde"
    steps = 10
    
    print("Copying Input to Comfy Input")
    #Copying split frames to ComfyUI input directory
    for frame in os.listdir(inputDir):
        if os.path.isfile(os.path.join(inputDir, frame)) and ( frame.endswith(".png") or frame.endswith(".jpg") ):
            copy(inputDir+frame, comfyInputDir+frame)

    #Creating a websocket to connect to the ComfyUI API
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    #Keeps track of which frame is being processed
    counter = 0
    previousFrame = ""

    #Every Frame in the ComfyUI input directory is generated
    for frame in sorted([f for f in os.listdir(comfyInputDir) if f.endswith('.png') or f.endswith('.jpg')], key=lambda x: int(x[5:-4])):
        if(counter == 0):
            previousFrame = frame
            counter = 1
        
        #Prints the current frame being generated
        print("Current Frame: "+frame+" Last Frame: "+previousFrame)
    
        # JSON used to set comfyui to generate
        prompt_text = {
            "3": {
                "inputs": {
                    "seed": 6,
                    "steps": steps,
                    "cfg": 8,
                    "sampler_name": sampler,
                    "scheduler": "normal",
                    "denoise": 0.30,
                    "model": [
                        "4",
                        0
                    ],
                    "positive": [
                        "6",
                        0
                    ],
                    "negative": [
                        "7",
                        0
                    ],
                    "latent_image": [
                        "11",
                        0
                    ]
                },
                "class_type": "KSampler",
                "_meta": {
                    "title": "KSampler"
                }
            },
            "4": {
                "inputs": {
                    "ckpt_name": modelName
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {
                    "title": "Load Checkpoint"
                }
            },
            "6": {
                "inputs": {
                    "text": enteredPrompt,
                    "clip": [
                        "4",
                        1
                    ]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Prompt)"
                }
            },
            "7": {
                "inputs": {
                    "text": enteredNegativePrompt,
                    "clip": [
                        "4",
                        1
                    ]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {
                    "title": "CLIP Text Encode (Prompt)"
                }
            },
            "8": {
                "inputs": {
                    "samples": [
                        "3",
                        0
                    ],
                    "vae": [
                        "4",
                        2
                    ]
                },
                "class_type": "VAEDecode",
                "_meta": {
                    "title": "VAE Decode"
                }
            },
            "9": {
                "inputs": {
                    "filename_prefix": frame,
                    "images": [
                        "8",
                        0
                    ]
                },
                "class_type": "SaveImage",
                "_meta": {
                    "title": "Save Image"
                }
            },
            "10": {
                "inputs": {
                    "image": frame,
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "11": {
                "inputs": {
                    "pixels": [
                        "13",
                        0
                    ],
                    "vae": [
                        "4",
                        2
                    ]
                },
                "class_type": "VAEEncode",
                "_meta": {
                    "title": "VAE Encode"
                }
            },
            "12": {
                "inputs": {
                    "image": previousFrame,
                    "upload": "image"
                },
                "class_type": "LoadImage",
                "_meta": {
                    "title": "Load Image"
                }
            },
            "13": {
                "inputs": {
                    "blend_factor": 0.3,
                    "blend_mode": "normal",
                    "image1": [
                        "10",
                        0
                    ],
                    "image2": [
                        "12",
                        0
                    ]
                },
                "class_type": "ImageBlend",
                "_meta": {
                    "title": "ImageBlend"
                }
            }
        }
        
        #Keeps track of previous frame for blending
        previousFrame = frame

        #Converts dict to json
        prompt_json = json.dumps(prompt_text)
        prompt = json.loads(prompt_json)
        
        #Generate
        images = get_images(ws, prompt)
    
    #Once all images are finished it copies them over
    for frame in os.listdir(comfyOutputDir):
        if os.path.isfile(os.path.join(comfyOutputDir, frame)) and frame.endswith(".png"):
            currentFrame = split('[.]', frame)[0]+".png"
            print("Copying "+frame+" to target directory as "+currentFrame)
            copy(comfyOutputDir+frame, outputDir+currentFrame)
            

#Used to set prompt with api call
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

#Used to start image generation
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output

    return output_images