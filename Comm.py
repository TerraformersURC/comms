import socket
import pickle
import zlib

class Comm:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        
    def send(self, data):
        try:
            self.sock.sendall(data)
        except socket.error as err:
            print(f'Error sending data: {err}')
            self.sock.close()

    def receive(self):
        try:
            data = self.sock.recv(1024 * 1024)  # Assuming larger buffer size for general data
            return data
        except socket.error as err:
            print(f'Error receiving data: {err}')
            self.sock.close()

    def send_video(self, frame):
        try:
            # Serialize and compress the frame
            compressed_frame = zlib.compress(pickle.dumps(frame))
            # Send the compressed frame
            self.send(compressed_frame)
        except Exception as e:
            print(f"Failed to send video frame: {e}")

    def receive_video(self):
        try:
            # Receive the compressed frame
            compressed_frame = self.receive()
            # Decompress and deserialize the frame
            if compressed_frame:
                frame = pickle.loads(zlib.decompress(compressed_frame))
                return frame
        except Exception as e:
            print(f"Failed to receive video frame: {e}")

    def close(self):
        self.sock.close()
        print("Connection closed.")
