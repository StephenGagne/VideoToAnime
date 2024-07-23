import unittest
from unittest.mock import patch, MagicMock
import websocket
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ai_image_generation import ai_generate, queue_prompt, get_images  

class TestAIGenerate(unittest.TestCase):
    @patch('app.ai_image_generation.os.listdir')
    @patch('app.ai_image_generation.shutil.copy')
    @patch('app.ai_image_generation.websocket.WebSocket')
    @patch('app.ai_image_generation.queue_prompt')
    @patch('app.ai_image_generation.get_images')
    def test_ai_generate(self, mock_get_images, mock_queue_prompt, mock_WebSocket, mock_copy, mock_listdir):
        # Mock return values
        mock_listdir.return_value = ['frame1.png', 'frame2.png']
        mock_copy.return_value = None
        mock_queue_prompt.return_value = {'prompt_id': 'test_id'}
        
        # Create a mock WebSocket instance
        mock_ws_instance = MagicMock()
        mock_WebSocket.return_value = mock_ws_instance
        mock_get_images.return_value = {'save_image_websocket_node': ['image_data']}
        
        # Call the function
        ai_generate("test_prompt", "test_negative_prompt", "test_model.ckpt", "ddim", 10)
        
        # Assertions to check if methods were called correctly
        mock_copy.assert_any_call('C:\\VideoToAnime\\originalFrames\\frame1.png', 'C:\\ComfyUI_windows_portable\\ComfyUI\\input\\frame1.png')
        mock_copy.assert_any_call('C:\\VideoToAnime\\originalFrames\\frame2.png', 'C:\\ComfyUI_windows_portable\\ComfyUI\\input\\frame2.png')
        mock_WebSocket.assert_called_once()
        mock_ws_instance.connect.assert_called_once_with("ws://127.0.0.1:8188/ws?clientId={}".format(client_id))
        mock_get_images.assert_called_once()

    @patch('app.ai_image_generation.urllib.request.urlopen')
    def test_queue_prompt(self, mock_urlopen):
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'prompt_id': 'test_id'}).encode('utf-8')
        mock_urlopen.return_value = mock_response
        
        # Call the function
        result = queue_prompt("test_prompt")
        
        # Assertions to check if the request was made correctly
        mock_urlopen.assert_called_once()
        self.assertEqual(result, {'prompt_id': 'test_id'})
        
    @patch('app.ai_image_generation.websocket.WebSocket.recv')
    @patch('app.ai_image_generation.queue_prompt')
    def test_get_images(self, mock_queue_prompt, mock_recv):
        # Mock return values
        mock_queue_prompt.return_value = {'prompt_id': 'test_id'}
        mock_recv.side_effect = [
            json.dumps({'type': 'executing', 'data': {'prompt_id': 'test_id', 'node': 'save_image_websocket_node'}}),
            json.dumps({'type': 'executing', 'data': {'prompt_id': 'test_id', 'node': None}}),
            b'image_data'
        ]
        
        # Create WebSocket instance
        ws = websocket.WebSocket()
        
        # Call the function
        result = get_images(ws, {'test': 'prompt'})
        
        # Assertions to check if images were received correctly
        self.assertIn('save_image_websocket_node', result)
        self.assertEqual(result['save_image_websocket_node'], ['image_data'])

if __name__ == '__main__':
    unittest.main()
