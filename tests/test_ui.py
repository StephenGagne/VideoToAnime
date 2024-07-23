import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ui import MyWindow

class TestMyWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = MyWindow()

    def tearDown(self):
        self.window.close()

    def test_window_initialization(self):
        self.assertEqual(self.window.windowTitle(), "Project - Group 8")
        self.assertEqual(self.window.width(), 400)
        self.assertEqual(self.window.height(), 450)
        self.assertFalse(self.window.isResizable())
        
    def test_upload_button(self):
        self.assertEqual(self.window.uploadButton.text(), "Upload")
        self.assertEqual(self.window.uploadButton.toolTip(), "Upload a video to be processed")
        
    def test_config_button(self):
        self.assertEqual(self.window.configButton.text(), "Config")
        self.assertEqual(self.window.configButton.toolTip(), "Set or change image generation options")
        
    def test_prompt_texts(self):
        self.assertEqual(self.window.positive_prompt_text.text(), "Positive Prompts: ")
        self.assertEqual(self.window.negative_prompt_text.text(), "Negative Prompts: ")
        
    def test_start_button(self):
        self.assertEqual(self.window.startButton.text(), "Start")
        self.assertEqual(self.window.startButton.toolTip(), "Initiate the conversion process")
        self.assertFalse(self.window.startButton.isEnabled())
        
    def test_properties_button(self):
        self.assertEqual(self.window.properties.text(), "Project Properties")
        self.assertEqual(self.window.properties.toolTip(), "Show project properties, including the current video and system properties")
        
    def test_recover_detected(self):
        self.window.recoverDetected()
        self.assertFalse(self.window.uploadButton.isVisible())
        self.assertFalse(self.window.configButton.isVisible())
        self.assertFalse(self.window.positive_prompt_text.isVisible())
        self.assertFalse(self.window.positive_prompt.isVisible())
        self.assertFalse(self.window.negative_prompt_text.isVisible())
        self.assertFalse(self.window.negative_prompt.isVisible())
        self.assertFalse(self.window.startButton.isVisible())
        self.assertFalse(self.window.properties.isVisible())
        
        self.assertTrue(self.window.recover_label_1.isVisible())
        self.assertTrue(self.window.recover_label_2.isVisible())
        self.assertTrue(self.window.recover_yes.isVisible())
        self.assertTrue(self.window.recover_no.isVisible())
        self.assertTrue(self.window.recover_thumbnail.isVisible())

if __name__ == "__main__":
    unittest.main()
