# AnimateXpress
Desktop tool for converting live-action video to animated

## Installation Guide
### Installing Stable Diffusion Automatic1111
1. Download `sd.webui.zip` from [v1.0.0-pre](https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases/tag/v1.0.0-pre)
2. Extract all
3. Run `update.bat`
4. Edit web-ui/webui-user.bat to include `COMMANDLINE_ARGS= --api`
You can find other installation guides at [Automatic1111 webui github](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

## Installing AnimateXpress
1. Download git
2. Download python 3.10.6
3. In a desired directory run `git clone https://github.com/aramalexanian/VideoToAnime.git`
4. Install pip `python -m ensurepip`
5. Update pip `pip install --upgrade pip`
6. Run `pip install -r requirements.txt`
7. Navigate to the `app` directory
8. Edit directory.py SDDIR="`Your Automatic1111 webui model directory`" example=`C:\AnimateXpress\sd.webui\webui\models\Stable-diffusion`
9. Move any Stable Diffusion models you plan on using into the Automatic1111 webui model directory

# Running AnimateXpress
1. Run Automatic1111 webui with `run.bat`
2. Run AnimateXpress with `start.bat`
3. Change the Stable Diffusion Checkpoint in the webui found in the top left of `http://127.0.0.1:7860/` to your desired style

# Using AnimateXpress
1. Upload a Video
2. Select a model
3. Change settings to the recommended settings for that model. Usually found on the download page.
4. Input a positive and negative prompt
5. Click Generate Video

# Settings Definitions
- Model: 			A Stable Diffusion model used to generate the new images
- Sampler: 		The sampler used to predict how to generate the new images
- Steps: 			The number of samples that each images needs to generate
- CFG: 			How creative the AI model is allowed to be (Lower = More creative)
- Denoise: 		How close to the original image the generated image will be (Lower = Closer to the original)
- Descale: 		Will reduce the dimensions of the input video. 0.50 = 50% of the original video
- Upscale:			Will increase the scale of the video in either 720p, 1080p, 4K or 8K
- Positive Prompt: This is what the AI will use to determine what to generate (What you expect to be in your generated video)
- Negative Prompt: This is what you want to avoid being in your video

# Prompt Examples
- Positive Prompt: (best quality, masterpiece), a white man with brown short hair and a brown beard
- Negative Prompt: (worst quality, low quality, letterboxed)