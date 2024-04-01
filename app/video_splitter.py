# Logic for splitting video into frames goes here
# Author: Xiaohang Ji and Chang Liu

import cv2
import os
import sys

if len(sys.argv) == 1 :
    print("No video name passed... exitting.")
    exit()
elif len(sys.argv) > 2 :
    print("Too many arguments... exitting.")
    exit()
    
videoName = sys.argv[1]

if not videoName.endswith((".mp4")):
    print("Incorrect video format... exitting")
    exit()

# Playing video from file:
# you can modify the "PutVideoName.mp4" to the video u wanna split
cap = cv2.VideoCapture('..\\input\\' + videoName)

try:
    # Create target Directory if not exist
    if not os.path.exists('..\\originalFrames'):
        os.makedirs('..\\originalFrames')
except OSError:
    print('Error: Creating directory of originalFrames')

currentFrame = 0
while(True):
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
    if not frame is None:
        cv2.imwrite(name, frame)
    else:
        print("Empty frame encountered")

    currentFrame += 1

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
