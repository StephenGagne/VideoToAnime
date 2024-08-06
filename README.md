# AnimateXpress
Desktop tool for converting live-action video to animated

## Installation Guide
### Installing Stable Diffusion Automatic1111
1. Download `sd.webui.zip` from [v1.0.0-pre](https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases/tag/v1.0.0-pre)
2. Extract all
3. Run `update.bat`
4. Edit web-ui/webui-user.bat to include `--api` in `COMMANDLINE_ARGS=`
5. Run `run.bat`
You can find other installation guides at [Automatic1111 webui github](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

## Installing AnimateXpress
1. Download git
2. Download python 3.10.6
3. In a desired directory run `git clone https://github.com/aramalexanian/VideoToAnime.git`
4. Install pip `python -m ensurepip`
5. Update pip `pip install --upgrade pip`
6. Run `pip install -r requirements.txt`

# Running AnimateXpress
1. Move into the `app` directory
2. Edit directory.py SDDIR="`Your Automatic1111 webui model directory`" example=`C:\AnimateXpress\sd.webui\webui\models\Stable-diffusion`
3. Move any Stable Diffusion models you plan on using into the Automatic1111 webui model directory
4. Change the Stable Diffusion Checkpoint in the webui found in the top left of `http://127.0.0.1:7860/` to your desired style
5. Run `ui.py`

# Using AnimateXpress
1. Upload a Video
2. Select a model
3. Change settings to the recommended settings for that model. Usually found on the download page.
4. Input a positive and negative prompt
5. Click Generate Video