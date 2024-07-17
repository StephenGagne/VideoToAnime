import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

# Add the root directory of the project to the Python path so the app could be an importable module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.audio_extractor import extract_audio

class TestAudioExtractor(unittest.TestCase):
    @patch('app.audio_extractor.os.makedirs')
    @patch('app.audio_extractor.os.path.exists')
    @patch('app.audio_extractor.VideoFileClip')
    def test_extract_audio(self, mock_videofileclip, mock_path_exists, mock_makedirs):
        # Mock the os.path.exists to always return True
        mock_path_exists.side_effect = lambda path: path.endswith('.mp4')

        # Mock the VideoFileClip object and its methods
        mock_video = MagicMock()
        mock_audio = MagicMock()
        mock_video.audio = mock_audio
        mock_videofileclip.return_value = mock_video

        # Run the function with a temporary video file path
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, 'test_video.mp4')
            with open(video_path, 'w') as f:
                f.write('test')  # Create a temporary file to simulate the video file

            extract_audio(video_path)

        # Assertions
        mock_path_exists.assert_any_call(video_path)
        self.assertTrue(mock_path_exists.called)
        mock_videofileclip.assert_called_once_with(video_path)
        mock_audio.write_audiofile.assert_called_once()
        mock_makedirs.assert_called_once()
        print("Test for extract_audio passed.")

if __name__ == '__main__':
    unittest.main()
