import unittest
import socket
import cv2
import numpy as np
from unittest.mock import patch, mock_open

from client import int_to_bytes, bytes_to_int, preprocess_image, send_images

class TestClient(unittest.TestCase):
    def test_int_to_bytes(self):
        self.assertEqual(int_to_bytes(1024), b'\x00\x00\x04\x00')
        self.assertEqual(int_to_bytes(0), b'\x00\x00\x00\x00')

    def test_bytes_to_int(self):
        self.assertEqual(bytes_to_int(b'\x00\x00\x04\x00'), 1024)
        self.assertEqual(bytes_to_int(b'\x00\x00\x00\x00'), 0)

    @patch('cv2.imread')
    @patch('cv2.resize')
    @patch('cv2.imencode')
    def test_preprocess_image(self, mock_imencode, mock_resize, mock_imread):
        mock_imread.return_value = np.zeros((300, 300, 3), np.uint8)
        mock_resize.return_value = np.zeros((300, 300), np.uint8)
        mock_imencode.return_value = (None, np.zeros((1, ), np.uint8))
        image_data = preprocess_image(r"C:\Users\nourn\OneDrive\Desktop\Semester 8\Distributed Computing\Trial\6.png")
        self.assertIsNotNone(image_data)

    @patch('socket.socket')
    def test_send_images(self, mock_socket):
        mock_socket.return_value.connect.return_value = None
        mock_socket.return_value.sendall.return_value = None
        mock_socket.return_value.recv.side_effect = [
            b'\x00\x00\x00\x64',
            b'\x00\x00\x00\x00'
        ]
        send_images('127.0.0.1', 12345, ['test_image.jpg'], 'edge_detection')
        mock_socket.return_value.connect.assert_called_with(('127.0.0.1', 12345))

if __name__ == '__main__':
    unittest.main()