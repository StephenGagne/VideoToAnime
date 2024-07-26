import cv2
import os
from audio_merger import merge_audio_to_video
from audio_extractor import extract_audio

def get_frame_rate(videoPath):
    # Get the frame rate
    frame_rate = cv2.VideoCapture(videoPath).get(cv2.CAP_PROP_FPS)
    return frame_rate

def stitch_frames(videoName,videoPath):
    # Path to the directory containing frames
    frame_directory = "..\\generatedFrames\\"
    # Temp video file to hold the video stitched
    temp_video_file = "..\\output\\temp_"+videoName+".mov"
    # Output video file name
    output_video_file = "..\\output\\"+videoName+".mov"
    # Frame rate from the input video
    frame_rate = get_frame_rate(videoPath)
    # Extract audio from input video
    extract_audio(videoPath)
    # Audio path
    audio_path = "..\\audio\\"+videoName+".mp3"
    # Get list of frame files in the directory, sorted by frame number
    frame_files = sorted([f for f in os.listdir(frame_directory) if f.endswith('.png') or f.endswith('.jpg')], key=lambda x: int(x[5:-4]))

    # Read the first frame to get the frame size
    first_frame = cv2.imread(os.path.join(frame_directory, frame_files[0]))
    height, width, layers = first_frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Note: for .mov files, 'mp4v' codec is commonly used
    video = cv2.VideoWriter(temp_video_file, fourcc, frame_rate, (width, height))

    # Iterate over each frame file and write it to the video
    for frame_file in frame_files:
        frame_path = os.path.join(frame_directory, frame_file)
        frame = cv2.imread(frame_path)
        video.write(frame)

    # Release the VideoWriter object
    video.release()
    # Merge audio with the created video
    merge_audio_to_video(temp_video_file, audio_path, output_video_file)
    os.remove(temp_video_file)
    print("Video has been created successfully!")

if __name__ == "__main__":
    video_name = "tenSeconds"
    video_path = "D:\\repo\\VideoToAnime\\input\\tenSeconds.mp4"
    audio_path = "..\\audio\\tenSeconds.mp3"
    stitch_frames(video_name, video_path)