import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import cv2
import tempfile
import sys

# Add the root directory of the project to the Python path so the app could be a importable module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.frame_stitcher import stitch_frames

class TestFrameStitcher(unittest.TestCase):
    @patch('app.frame_stitcher.os.listdir')
    @patch('app.frame_stitcher.cv2.imread')
    @patch('app.frame_stitcher.cv2.VideoWriter')
    def test_stitch_frames(self, mock_videowriter, mock_imread, mock_listdir):
        # Mock the list of frame files
        mock_listdir.return_value = ['frame1.png', 'frame2.png', 'frame3.png']
        
        # Mock the read frames
        mock_frame = MagicMock()
        mock_frame.shape = (480, 640, 3)
        mock_imread.return_value = mock_frame
        
        # Mock the VideoWriter object
        mock_video = MagicMock()
        mock_videowriter.return_value = mock_video
        
        # Run the function
        with tempfile.TemporaryDirectory() as temp_dir:
            generated_frames_dir = os.path.join(temp_dir, 'generatedFrames')
            os.mkdir(generated_frames_dir)
            output_dir = os.path.join(temp_dir, 'output')
            os.mkdir(output_dir)
            
            # Create mock frame files
            for frame in mock_listdir.return_value:
                with open(os.path.join(generated_frames_dir, frame), 'w') as f:
                    f.write('test')
            
            stitch_frames('test_video')
        
        # Assertions
        mock_listdir.assert_called_once_with('..\\generatedFrames\\')
        self.assertEqual(mock_imread.call_count, 4)
        self.assertEqual(mock_video.write.call_count, 3)
        mock_video.release.assert_called_once()
        print("Test for stitch_frames passed.")

if __name__ == '__main__':
    unittest.main()
