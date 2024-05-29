import cv2
import os

def merge_frames_into_video(frame_directory, output_video_file, frame_rate=30.0):

    # Get list of frame files in the directory, sorted by frame number
    frame_files = sorted([f for f in os.listdir(frame_directory) if f.endswith('.jpg')], key=lambda x: int(x[6:-4]))

    if not frame_files:
        print("No frames found in the directory.")
        return

    # Read the first frame to get the frame size
    first_frame = cv2.imread(os.path.join(frame_directory, frame_files[0]))
    height, width, layers = first_frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Note: for .mov files, 'mp4v' codec is commonly used
    video = cv2.VideoWriter(output_video_file, fourcc, frame_rate, (width, height))

    # Iterate over each frame file and write it to the video
    for frame_file in frame_files:
        frame_path = os.path.join(frame_directory, frame_file)
        frame = cv2.imread(frame_path)
        video.write(frame)

    # Release the VideoWriter object
    video.release()
    print("Video has been created successfully!")

# Example usage
frame_directory = 'output_frames'
output_video_file = 'output_video.mov'
merge_frames_into_video(frame_directory, output_video_file)
