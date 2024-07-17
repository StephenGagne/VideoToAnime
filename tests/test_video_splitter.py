import unittest
from unittest.mock import patch, MagicMock
import os
import cv2
import tempfile
import sys

# Add the root directory of the project to the Python path so the app could be an importable module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.video_splitter import split

class TestVideoSplitter(unittest.TestCase):
    @patch('app.video_splitter.os.makedirs')
    @patch('app.video_splitter.os.path.exists')
    @patch('app.video_splitter.cv2.VideoCapture')
    @patch('app.video_splitter.cv2.imwrite')
    def test_split(self, mock_imwrite, mock_videocapture, mock_path_exists, mock_makedirs):
        # Mock the os.path.exists to always return False
        mock_path_exists.return_value = False

        # Mock the VideoCapture object and its methods
        mock_cap = MagicMock()
        mock_videocapture.return_value = mock_cap
        mock_cap.read.side_effect = [(True, MagicMock()), (True, MagicMock()), (False, None)]  # Two frames then end

        # Run the function
        with tempfile.TemporaryDirectory() as temp_dir:
            original_frames_dir = os.path.join(temp_dir, 'originalFrames')
            os.mkdir(original_frames_dir)

            split('test_video.mp4')

        # Assertions
        mock_path_exists.assert_called_once_with('..\\originalFrames')
        mock_makedirs.assert_called_once_with('..\\originalFrames')
        self.assertEqual(mock_imwrite.call_count, 2)  # Two frames written
        mock_cap.release.assert_called_once()
        print("Test for split passed.")

if __name__ == '__main__':
    unittest.main()
