import sys
import os
import sdkit
from sdkit.models import load_model
from sdkit.generate import generate_images
from sdkit.utils import log

if(len(sys.argv) < 2):
    enteredPrompt = 'max fleischer style, a photo of a man shooting a gun'
else:
    enteredPrompt = sys.argv[1]
    
if(len(sys.argv) < 3):
    enteredNegativePrompt = ' '
else:
    enteredNegativePrompt = sys.argv[2]

context = sdkit.Context()

# set the path to the model file on the disk (.ckpt or .safetensors file)
context.model_paths['stable-diffusion'] = '..\\config\\fleischerStyle_v1.ckpt'
load_model(context, 'stable-diffusion')

outputs = 1
frameDir = "..\\originalFrames\\"
targetDir = "..\\generatedFrames\\"
frames = []

for frame in os.listdir(frameDir):
    if os.path.isfile(os.path.join(frameDir, frame)) and frame.endswith((".jpg")):
        # generate the image
        images = generate_images(context, prompt=enteredPrompt, num_outputs=outputs, negative_prompt=enteredNegativePrompt, seed=42, width=550, height=550, sampler_name='plms', 
                         init_image=frameDir+frame, preserve_init_image_color_profile=True)

        # save the image

        for i in range(0, outputs):
            saveName = targetDir + frame
            images[i].save(saveName) # images is a list of PIL.Image

log.info("Generated images!")