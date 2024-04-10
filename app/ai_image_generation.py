import sys
import os
import sdkit
from sdkit.models import load_model
from sdkit.generate import generate_images
from sdkit.utils import log

######################## ARGUMENT PROCESSING ###########################

# Looks for an entered positive prompt (First argument)
if(len(sys.argv) < 2):
    enteredPrompt = 'max fleischer style, a photo of a man shooting a gun'
else:
    enteredPrompt = sys.argv[1]
    
# Looks for an enetered negative prompt (Second argument)
if(len(sys.argv) < 3):
    enteredNegativePrompt = ' '
else:
    enteredNegativePrompt = sys.argv[2]
    
############################## MODEL SPECIFICATION ###########################

context = sdkit.Context()

# set the path to the model file on the disk (.ckpt or .safetensors file)
context.model_paths['stable-diffusion'] = '..\\config\\fleischerStyle_v1.ckpt'
load_model(context, 'stable-diffusion')



############################## IMAGE GENERATION ################################
# Number of frames to output per input
outputs = 1
# Directory of frames to be processed
frameDir = "..\\originalFrames\\"
# Target directory for proocessed frames
targetDir = "..\\generatedFrames\\"

# Loops through all frames found in the originalFrames directoryd
for frame in os.listdir(frameDir):
    if os.path.isfile(os.path.join(frameDir, frame)) and frame.endswith((".jpg")):
        # generates the image from the frame
        images = generate_images(context, prompt=enteredPrompt, num_outputs=outputs, negative_prompt=enteredNegativePrompt, width=550, height=550, sampler_name='dpmpp_sde', 
                         init_image=frameDir+frame, preserve_init_image_color_profile=True, prompt_strength=0.38)

        # save the generated image in the generatedFrames directory

        for i in range(0, outputs):
            saveName = targetDir + frame
            images[i].save(saveName) # images is a list of PIL.Image

log.info("Generated images!")