import socket
import cv2
import numpy as np
import pyrealsense2 as rs

class Comm:

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((ip, port))
        except socket.error as err:
            print(f"Error connecting to {ip}:{port}: {err}")
            self.sock.close()

    def send(self, message):
        try:
            # Send data
            self.sock.sendall(message.encode())
            print(f"Sent: {message}")
        except Exception as err:
            print(f'Error sending message: {err}')

    def receive(self):
        try:
            # Receive data (assuming a maximum message size of 1024 bytes)
            received_data = self.sock.recv(1024)

            # Decode the received data (assuming UTF-8 encoding)
            message = received_data.decode()

            print(f"Received message: {message}")

        except socket.error as err:
            print(f"Error receiving message: {err}")

    def send_video(self, pipeline):
        try:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                return

            # Convert color frame to numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Serialize frame to bytes
            encoded_frame = cv2.imencode('.jpg', color_image)[1].tobytes()

            # Send the length of the frame first
            length = len(encoded_frame)
            self.sock.sendall(length.to_bytes(4, byteorder='big'))

            # Send the frame data
            self.sock.sendall(encoded_frame)
            print("Sent video frame")
        except Exception as err:
            print(f"Error sending video frame: {err}")

    def receive_video(self):
        try:
            # Receive the length of the frame
            length_bytes = self.sock.recv(4)
            length = int.from_bytes(length_bytes, byteorder='big')

            # Receive the frame data
            frame_data = b''
            while len(frame_data) < length:
                frame_data += self.sock.recv(length - len(frame_data))

            # Decode frame data
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('Received Video', frame)
            cv2.waitKey(1)
        except Exception as err:
            print(f"Error receiving video frame: {err}")