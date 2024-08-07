import urllib.request
import base64
import json
import time
import os
import cv2 
from PIL import Image

#Global Variables
webui_server_url = 'http://localhost:7860'
out_dir = '../'
out_dir_i2i = os.path.join(out_dir, 'generatedFrames')
os.makedirs(out_dir_i2i, exist_ok=True)
inputDir = "../originalFrames/"

##
# Encodes an image to base64
# path = path to file
# return = the image that is encoded
##
def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

##
# Decodes a string to an image
# base64_str = received string
# save_path = path to save decoded file
##
def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))

##
# Calls an api endpoint (127.0.0.1/sdapi/v1/img2img)
# api_endpoint = the end point being called
# **payload = the payload being sent in json format
# return = the image that is received
##
def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


##
# Used to call the img2img api with a payload and receive the created image
# savePath = path to save the file
# **payload = the payload being sent to the api in json format
##
def call_img2img_api(savePath, **payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')):
        decode_and_save_base64(image, savePath)


##
# Creates a json object to send to the api for img2img generation
# positive = the positive prompt
# negative = the negative prompt
# steps = the number of steps for the sampler
# cfg = the cfg value
# denoise = the denoise value
# imagePath = the path to the image
# descale = the descale value
# model_name = the name of the model
# sampler = the name of the sampler
# return = The payload that is created
##
def create_payload(positive, negative, steps, cfg, denoise, imagePath, descale, model_name, sampler):
    batch_size = 1
    
    #Opens the image to determine height and width
    tempImg = Image.open(imagePath)
    height = tempImg.height
    width = tempImg.width
    #Adjusts the output height and weight with the descale value
    height = height*descale
    width = width*descale
    
    #Encodes the image for json transportation
    init_images = [
        encode_file_to_base64(imagePath)
    ]
    
    payload = {
        "prompt": positive,
        "negative_prompt": negative,
        "seed": 1,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": sampler,
        "width": width,
        "height": height,
        "denoising_strength": denoise,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": batch_size if len(init_images) == 1 else len(init_images),
        "override_settings": {
             'sd_model_checkpoint': model_name,
        },
    }
    
    return payload


##
# Creates a json object to send to the api for upscaling
# positive = the positive prompt
# negative = the negative prompt
# imagePath = the path to the image
# model_name = the name of the model
# sampler = the name of the sampler
# upscale_value = the amount the image will be upscaled
# return = payload
##
def create_upscale_payload(positive, negative, imagePath, model_name, sampler, upscale_value):
    #Encodes image for transportation
    init_images = [
        encode_file_to_base64(imagePath)
    ]
    
    #opens image to determine height and width
    temp_img = Image.open(imagePath)
    img_width = temp_img.width
    img_height = temp_img.height
    upscale_quotient = 0
    
    #Determines the quotient for upscaling
    #Uses the height or width depending on which is greater
    if img_width > img_height:
        upscale_quotient = upscale_value/img_width
    else:
        upscale_quotient = upscale_value/img_height
    
    payload = {
        "sd_model_checkpoint":model_name,
        "sd_vae":"",
        "prompt":positive,
        "negative_prompt":negative,
        "cfg_scale": 15,
        "denoising_strength": 0.10,
        "init_images":init_images,
        "sampler_index":sampler,
        "steps":50,
        "script_name": "SD upscale",
        "script_args": ["", 64, "R-ESRGAN 4x+", upscale_quotient],
        "alwayson_scripts":{
        }
    }
    
    return payload


##
# Starts the image generation process for every file in the originalFrames/ directory
# positive = the positive prompt
# negative = the negative prompt
# model_name = the name of the model
# sampler = the name of the sampler
# steps = the number of steps for the sampler
# cfg = the cfg value
# denoise = the denoise value
# descale = the descale value
# upscale = whether upscaling is happening default to False
# upscale_name = the model used to upscale
# upscale_value = the amount that the video will be upscaled to
##
def generate_images(positive, negative, model_name, sampler, steps, cfg, denoise, descale, upscale=False, upscale_name="", upscale_value=1.5):
    counter = 0
    #Pulls all the frames from ../originalFrames/ in order and generates them
    for frame in sorted([f for f in os.listdir(inputDir) if f.endswith('.png') or f.endswith('.jpg')], key=lambda x: int(x[5:-4])):
        imagePath = os.path.join(inputDir, frame)
        payload = create_payload(positive, negative, steps, cfg, denoise, imagePath, descale, model_name, sampler)
        savePath = "../generatedFrames/"+frame
        call_img2img_api(savePath, **payload)
        #If upscaling is enabled it will pass the generated frame through upscaling
        if(upscale):
            imagePath = os.path.join(out_dir_i2i, frame)
            payload = create_upscale_payload(positive, negative, imagePath, upscale_name, sampler, upscale_value)
            savePath = "../generatedFrames/"+frame
            call_img2img_api(savePath, **payload)


##
# Used for when running the file on it's own for testing
##
if __name__ == '__main__':
    positive = "(best quality, masterpiece), a white man, brown short hair, brown beard"
    negative = "(worst quality, low quality, letterboxed)"
    model_name = "toonyou_beta3"
    upscale_name = "x4-upscaler-ema"
    steps = 15
    cfg = 8
    sampler = "Euler a"
    denoise = 0.40
    descale = 0.5
    upscale_value = 7680
    
    
    generate_images(positive, negative, model_name, sampler, steps, cfg, denoise, descale, True, upscale_name, upscale_value)
    