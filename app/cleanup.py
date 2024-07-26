import os

def cleanup():
    Generated = "../generatedFrames/"
    Split = "../originalFrames/"
        
    for filename in os.listdir(Generated):
        file_path = os.path.join(Generated, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
    for filename in os.listdir(Split):
        file_path = os.path.join(Split, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)