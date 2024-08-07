import os
from moviepy.editor import VideoFileClip, AudioFileClip

##
# Checks if the file exists
# file_path = path to the file being checked
##
def file_exists(file_path):
    """Check if a file exists."""
    return os.path.isfile(file_path)

##
# Checks if the video and audio are the same length
# video_path = path to the video
# audio_path = path to the audio
##
def check_lengths(video_path, audio_path):
    """Check if the lengths of the video and audio are the same."""
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    video_duration = video_clip.duration
    audio_duration = audio_clip.duration
    
    return video_duration == audio_duration

##
# Adds the audio to the video
# video_path = path to the video
# audio_path = path to the audio
# output_path = path to save the new video
##
def merge_audio_to_video(video_path, audio_path, output_path):
    """Merge an audio file to a video file if they exist and have the same length."""
    if not file_exists(video_path):
        print(f"Video file '{video_path}' does not exist.")
        return
    if not file_exists(audio_path):
        print(f"Audio file '{audio_path}' does not exist.")
        return
    
    # Load video clip
    video_clip = VideoFileClip(video_path)

    # Load audio clip
    audio_clip = AudioFileClip(audio_path)

    # Set audio of the video clip to the audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Write the output file
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    print(f"Successfully merged audio with video. Output saved at '{output_path}'")

# Example usage
# if __name__ == "__main__":
#     video_path = "..\\videoExtract\\tenSeconds_no_audio.mov"  # or .mov
#     audio_path = "..\\audio\\tenSeconds.mp3"
#     output_path = "..\\output\\video_with_audio.mov"  # or .mov

#     merge_audio_to_video(video_path, audio_path, output_path)
