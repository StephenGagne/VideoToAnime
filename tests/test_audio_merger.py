import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# Add the root directory of the project to the Python path so the app could be an importable module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.audio_merger import merge_audio_to_video, file_exists, check_lengths

class TestAudioMerger(unittest.TestCase):
    @patch('app.audio_merger.os.path.isfile')
    @patch('app.audio_merger.VideoFileClip')
    @patch('app.audio_merger.AudioFileClip')
    def test_merge_audio_to_video(self, mock_audioclip, mock_videoclip, mock_isfile):
        # Mock the os.path.isfile to always return True
        mock_isfile.return_value = True

        # Mock the VideoFileClip and AudioFileClip objects and their methods
        mock_video = MagicMock()
        mock_audio = MagicMock()
        mock_video.set_audio.return_value = mock_video
        mock_videoclip.return_value = mock_video
        mock_audioclip.return_value = mock_audio

        # Run the function with temporary file paths
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, 'test_video.mov')
            audio_path = os.path.join(temp_dir, 'test_audio.mp3')
            output_path = os.path.join(temp_dir, 'output_video.mov')
            
            with open(video_path, 'w') as f:
                f.write('test')  # Create a temporary file to simulate the video file
            with open(audio_path, 'w') as f:
                f.write('test')  # Create a temporary file to simulate the audio file

            merge_audio_to_video(video_path, audio_path, output_path)

        # Assertions
        mock_isfile.assert_any_call(video_path)
        mock_isfile.assert_any_call(audio_path)
        mock_videoclip.assert_called_once_with(video_path)
        mock_audioclip.assert_called_once_with(audio_path)
        mock_video.set_audio.assert_called_once_with(mock_audio)
        mock_video.write_videofile.assert_called_once_with(output_path, codec='libx264', audio_codec='aac')
        print("Test for merge_audio_to_video passed.")

if __name__ == '__main__':
    unittest.main()
