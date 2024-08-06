from moviepy.editor import VideoFileClip
import sys
import os

def extract_audio(video_name):
    # Ensure the input file exists
    input_video_path = video_name
    output_audio_dir = "../audio/"
    output_audio_path = os.path.join(output_audio_dir, f"{os.path.splitext(os.path.basename(video_name))[0]}.mp3")

    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"The file {input_video_path} does not exist.")
    
    # Ensure the file is an MP4 file
    if not input_video_path.lower().endswith('.mp4'):
        raise ValueError("The input file must be an MP4 file.")
    
    # Load the video file
    video = VideoFileClip(input_video_path)
    
    # Extract the audio
    audio = video.audio
    
    # Ensure the output directory exists
    os.makedirs(output_audio_dir, exist_ok=True)
    
    # Save the audio to a file
    audio.write_audiofile(output_audio_path)
    print(f"Audio extracted and saved to {output_audio_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audio_extractor.py <path_to_video>")
        sys.exit(1)

    video_path = sys.argv[1]

    try:
        extract_audio(video_path)
    except Exception as e:
        print(f"An error occurred: {e}")
