from moviepy.editor import VideoFileClip
import os

def extract_audio(video_name):
    # Ensure the input file exists

    input_video_path = video_name
    project_root = os.path.abspath(os.path.join(os.path.dirname(input_video_path), '..'))
    output_audio_path = os.path.join(project_root, 'audio', f"{os.path.splitext(os.path.basename(video_name))[0]}.mp3")

    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"The file {input_video_path} does not exist.")
    
    # Ensure the file is an MP4 file
    if not input_video_path.lower().endswith('.mp4'):
        raise ValueError("The input file must be an MP4 file.")
    
    # Load the video file
    video = VideoFileClip(input_video_path)
    
    # Extract the audio
    audio = video.audio
    
    # Save the audio to a file
    audio.write_audiofile(output_audio_path)
    print(f"Audio extracted and saved to {output_audio_path}")
