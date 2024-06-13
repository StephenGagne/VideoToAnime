import ffmpeg
import os

def merge_audio_to_video(video_path, audio_path, output_path):
    # Check if the input files exist
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Check if the output directory exists, if not create it
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Get video and audio duration
        video_info = ffmpeg.probe(video_path)
        audio_info = ffmpeg.probe(audio_path)
        video_duration = float(video_info['format']['duration'])
        audio_duration = float(audio_info['format']['duration'])

        # Adjust audio duration if it is shorter than video duration
        if audio_duration < video_duration:
            audio_filter = f"apad=pad_dur={video_duration}"
        else:
            audio_filter = None

        # Merge audio with video
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)
        
        if audio_filter:
            input_audio = input_audio.filter('apad', pad_dur=video_duration)
        
        ffmpeg.output(input_video, input_audio, output_path, vcodec='copy', acodec='aac', strict='experimental').run(overwrite_output=True)
        
        print(f"Merged video saved to {output_path}")

    except ffmpeg.Error as e:
        print(f"Error occurred: {e.stderr.decode()}")

if __name__ == "__main__":
    # Example usage
    video_path = "..\\videoExtract\\tenSeconds_no_audio.mov"
    audio_path = "..\\audio\\tenSeconds.mp3"
    output_path = "..\\output"

    merge_audio_to_video(video_path, audio_path, output_path)
