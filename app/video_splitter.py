# Logic for splitting video into frames goes here
# Author: Xiaohang Ji and Chang Liu

# UI LINK TEST

import cv2
import os

##
# Splits the video into frames
# video_name = name of the video
##
def split(video_name):
    # Playing video from file:
    # you can modify the "PutVideoName.mp4" to the video u wanna split
    cap = cv2.VideoCapture(video_name)
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
        name =  '..\\originalFrames\\frame' + str(currentFrame) + '.jpg'
        
        # Write the frame to disk if it's not empty
        if not frame is None:
            #Merge the last frame and the current frame 30% last 70% current
            if currentFrame != 0:
                lastName = '..\\originalFrames\\frame' + str(currentFrame-1) + '.jpg'
                lastFrame = cv2.imread(lastName) 

                frame = lastFrame * 0.3 + frame * 0.7
            cv2.imwrite(name, frame)
        else:
            print("Empty frame encountered")

        currentFrame += 1

    # When everything is done, release the capture
    cap.release()
    return

##
# Used for when running the file on it's own for testing
##
if __name__ == '__main__':
    split("C:\\VideoToAnime\\input\\example.mp4")