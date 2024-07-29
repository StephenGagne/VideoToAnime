import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Mock the missing modules
sys.modules['video_splitter'] = MagicMock()
sys.modules['ai_image_generation'] = MagicMock()
sys.modules['frame_stitcher'] = MagicMock()
sys.modules['cleanup'] = MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the os.listdir function to avoid FileNotFoundError
with patch('os.listdir', return_value=['model1', 'model2']):
    from app.ui import MyWindow  # Adjust the import based on your project structure

class TestMyWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = MyWindow()
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_initial_state(self):
        self.assertEqual(self.window.windowTitle(), "AnimateXpress")
        self.assertEqual(self.window.uploadButton.text(), "Upload Video")
        self.assertFalse(self.window.startButton.isEnabled())

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('dummy_video.mp4', ''))
    def test_upload_button(self, mock_getOpenFileName):
        QTest.mouseClick(self.window.uploadButton, Qt.LeftButton)
        self.assertTrue(self.window.startButton.isEnabled())
        self.assertEqual(self.window.__file, 'dummy_video.mp4')

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('dummy_video.mp4', ''))
    @patch.object(MyWindow, 'splitFrames')
    def test_generate_video_button_without_prompts(self, mock_splitFrames, mock_getOpenFileName):
        QTest.mouseClick(self.window.uploadButton, Qt.LeftButton)
        self.window.__file = "dummy_video.mp4"
        self.window.startButton.setEnabled(True)
        QTest.mouseClick(self.window.startButton, Qt.LeftButton)
        self.assertTrue(self.window.startButton.isEnabled())
        mock_splitFrames.assert_not_called()  # Ensures splitFrames is not called due to missing prompt

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', return_value=('dummy_video.mp4', ''))
    @patch.object(MyWindow, 'splitFrames')
    def test_generate_video_button_with_prompts(self, mock_splitFrames, mock_getOpenFileName):
        QTest.mouseClick(self.window.uploadButton, Qt.LeftButton)
        self.window.__file = "dummy_video.mp4"
        self.window.startButton.setEnabled(True)
        self.window.positive_prompt.setPlainText("Test Positive Prompt")
        QTest.mouseClick(self.window.startButton, Qt.LeftButton)
        mock_splitFrames.assert_called_once()  # Ensures splitFrames is called

    def test_upscale_checkbox(self):
        initial_height = self.window.height()
        QTest.mouseClick(self.window.upscale_checkbox, Qt.LeftButton)
        self.assertGreater(self.window.height(), initial_height)
        QTest.mouseClick(self.window.upscale_checkbox, Qt.LeftButton)
        self.assertEqual(self.window.height(), initial_height)

    def test_configure_model_and_sampler(self):
        self.window.model_combo.setCurrentIndex(1)
        self.assertEqual(self.window.model_combo.currentText(), self.window.models[1])

        self.window.sampler_combo.setCurrentIndex(1)
        self.assertEqual(self.window.sampler_combo.currentText(), self.window.samplers[1])

if __name__ == "__main__":
    unittest.main()
