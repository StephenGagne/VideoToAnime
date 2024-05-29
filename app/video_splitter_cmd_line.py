# Logic for splitting video into frames goes here
# Author: Xiaohang Ji and Chang Liu

# UI LINK TEST

import cv2
import os
import sys
from audio_extractor import extract_audio

if len(sys.argv) == 1:
    print("No video name passed... exiting.")
    exit()
elif len(sys.argv) > 2:
    print("Too many arguments... exiting.")
    exit()

videoName = sys.argv[1]

if not videoName.endswith((".mp4", ".mov")):
    print("Incorrect video format... exiting")
    exit()

input_video_path = os.path.join('..', 'input', videoName)
output_audio_path = os.path.join('..', 'audio', f"{os.path.splitext(videoName)[0]}.mp3")

# Ensure the output directory for audio exists
os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)

# Extract audio
try:
    extract_audio(input_video_path, output_audio_path)
except Exception as e:
    print(f"Error extracting audio: {e}")
    exit()

# Playing video from file:
cap = cv2.VideoCapture(input_video_path)

try:
    # Create target Directory if not exist
    if not os.path.exists('..\\originalFrames'):
        os.makedirs('..\\originalFrames')
except OSError:
    print('Error: Creating directory of originalFrames')

currentFrame = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if frame is empty (end of video)
    if not ret:
        print("End of video")
        break

    # Saves image of the current frame in jpg file
    name = '..\\originalFrames\\frame' + str(currentFrame) + '.jpg'
    print('Creating...' + name)
    
    # Write the frame to disk if it's not empty
    if frame is not None:
        cv2.imwrite(name, frame)
    else:
        print("Empty frame encountered")

    currentFrame += 1

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
