# Logic for splitting video into frames goes here
# Author: Xiaohang Ji and Chang Liu

# UI LINK TEST

import cv2
import os
import sys
from audio_extractor import extract_audio

def split(video_name):
    # Playing video from file:
    # you can modify the "PutVideoName.mp4" to the video u wanna split
    input_video_path = video_name
    project_root = os.path.abspath(os.path.join(os.path.dirname(input_video_path), '..'))
    output_audio_path = os.path.join(project_root, 'audio', f"{os.path.splitext(os.path.basename(video_name))[0]}.mp3")
    
    # Ensure the output directory for audio exists
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)

    # Extract audio
    try:
        extract_audio(input_video_path, output_audio_path)
    except Exception as e:
        print(f"Error extracting audio: {e}")
        exit()
    
    cap = cv2.VideoCapture(video_name)    
    try:
        # Create target Directory if not exist
        frames_dir = os.path.join(project_root, 'originalFrames')
        if not os.path.exists(frames_dir):
                    os.makedirs(frames_dir)
    except OSError as e:
        print(f'Error: Creating directory of originalFrames - {e}')

    currentFrame = 0
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is empty (end of video)
        if not ret:
            print("End of video")
            break

        # Saves image of the current frame in jpg file
        name = os.path.join(frames_dir, f'frame{currentFrame}.jpg')
        
        # Write the frame to disk if it's not empty
        if not frame is None:
            cv2.imwrite(name, frame)
        else:
            print("Empty frame encountered")

        currentFrame += 1

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return
