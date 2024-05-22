import sys
import os
import sdkit
from sdkit.models import load_model
from sdkit.generate import generate_images
from sdkit.utils import log

##
# Function to generate images
# enteredPrompt:            A prompt used to style each image
# enteredNegativePrompt     A prompt used to excluded certain data from each image
##

def ai_generate(enteredPrompt, enteredNegativePrompt):

    ############################## MODEL SPECIFICATION ###########################

    context = sdkit.Context()

    # set the path to the model file on the disk (.ckpt or .safetensors file)
    context.model_paths['stable-diffusion'] = '..\\config\\drippyWatercolor_jwlWatercolorDrippy.ckpt'
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