from datetime import datetime
import urllib.request
import base64
import json
import time
import os
import cv2 
from PIL import Image

webui_server_url = 'http://localhost:7860'

out_dir = '../'
out_dir_i2i = os.path.join(out_dir, 'generatedFrames')
os.makedirs(out_dir_i2i, exist_ok=True)
inputDir = "C:\\VideoToAnime\\originalFrames\\"
mergedDir = "merged"
os.makedirs(mergedDir, exist_ok=True)


def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def call_img2img_api(savePath, **payload):
    response = call_api('sdapi/v1/img2img', **payload)
    for index, image in enumerate(response.get('images')):
        decode_and_save_base64(image, savePath)
        
def create_payload(positive, negative, steps, cfg, denoise, imagePath, descale, model_name, sampler):
    batch_size = 1
    
    tempImg = Image.open(imagePath)
    
    height = tempImg.height
    height = height*descale
    width = tempImg.width
    width = width*descale
    
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
    
def image_merge(previousImage, currentImage, frame):
    image1 = cv2.imread(previousImage) 
    image2 = cv2.imread(currentImage) 

    image3 = image1 * 0.3 + image2 * 0.7
    
    outputDirectory = os.path.join(mergedDir, frame)
    cv2.imwrite(outputDirectory, image3)
    
def create_upscale_payload(positive, negative, imagePath, model_name, sampler):
    init_images = [
        encode_file_to_base64(imagePath)
    ]
    
    payload = {
        "sd_model_checkpoint":model_name,
        "sd_vae":"",
        "prompt":positive,
        "negative_prompt":negative,
        "denoising_strength": 0.20,
        "init_images":init_images,
        "sampler_index":sampler,
        "steps":40,
        "script_name": "SD upscale",
        "script_args": ["", 64, "R-ESRGAN 4x+", 1.5],
        "alwayson_scripts":{
        }
    }
    
    return payload

def generate_images(positive, negative, model_name, sampler, steps, cfg, denoise, descale, upscale=False, upscale_name="", upscale_loops=1):
    counter = 0
    previousImage = ""
    for frame in sorted([f for f in os.listdir(inputDir) if f.endswith('.png') or f.endswith('.jpg')], key=lambda x: int(x[5:-4])):
        imagePath = os.path.join(inputDir, frame)
    
        if(counter == 0):
            previousImage = imagePath
            counter = 1
            
        image_merge(previousImage, imagePath, frame)
        
        previousImage = imagePath

    #Every Frame sorted
    for frame in sorted([f for f in os.listdir(mergedDir) if f.endswith('.png') or f.endswith('.jpg')], key=lambda x: int(x[5:-4])):
        imagePath = os.path.join(mergedDir, frame)
        payload = create_payload(positive, negative, steps, cfg, denoise, imagePath, descale, model_name, sampler)
        savePath = "../generatedFrames/"+frame
        call_img2img_api(savePath, **payload)
        if(upscale):
            upscales = 0
            while upscale_loops > upscales:
                imagePath = os.path.join(out_dir_i2i, frame)
                payload = create_upscale_payload(positive, negative, imagePath, upscale_name, sampler)
                savePath = "../generatedFrames/"+frame
                call_img2img_api(savePath, **payload)
                upscales = upscales + 1

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
    
    
    generate_images(positive, negative, model_name, sampler, steps, cfg, denoise, descale, True, upscale_name)
    