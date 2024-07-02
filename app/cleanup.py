import os

def cleanup():
    ComfyInputs = "C:\\ComfyUI_windows_portable\\ComfyUI\\input"
    ComfyOutputs = "C:\\ComfyUI_windows_portable\\ComfyUI\\output"
    Generated = "C:\\VideoToAnime\\generatedFrames"
    Split = "C:\\VideoToAnime\\originalFrames"

    for filename in os.listdir(ComfyInputs):
        file_path = os.path.join(ComfyInputs, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
    for filename in os.listdir(ComfyOutputs):
        file_path = os.path.join(ComfyOutputs, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
        
    for filename in os.listdir(Generated):
        file_path = os.path.join(Generated, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
    for filename in os.listdir(Split):
        file_path = os.path.join(Split, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)