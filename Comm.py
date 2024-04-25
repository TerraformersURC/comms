import socket
import pickle
import zlib

class Comm:
    def __init__(self, mode, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mode = mode
        if mode == 'server':
            self.sock.bind((ip, port))
            self.sock.listen(1)
            print(f"Server listening on {ip}:{port}")
            self.conn, self.addr = self.sock.accept()
            print(f"Connected by {self.addr}")
        elif mode == 'client':
            try:
                self.sock.connect((ip, port))
                print(f"Connected to server at {ip}:{port}")
            except socket.error as err:
                print(f"Error connecting to server: {err}")
                self.sock.close()
                raise

    def send(self, data):
        if self.mode == 'client':
            try:
                self.sock.sendall(data)
            except socket.error as err:
                print(f'Error sending data: {err}')
                self.sock.close()
        elif self.mode == 'server':
            try:
                self.conn.sendall(data)
            except socket.error as err:
                print(f'Error sending data: {err}')
                self.conn.close()

    def receive(self):
        if self.mode == 'client':
            try:
                data = self.sock.recv(1000*1000*255*3)  # Buffer size can be adjusted
                return data
            except socket.error as err:
                print(f'Error receiving data: {err}')
                self.sock.close()
        elif self.mode == 'server':
            try:
                data = self.conn.recv(1000*1000*255*3)  # Buffer size can be adjusted
                return data
            except socket.error as err:
                print(f'Error receiving data: {err}')
                self.conn.close()

    def send_video(self, frame):
        try:
            compressed_frame = pickle.dumps(frame)
            self.send(compressed_frame)
        except Exception as e:
            print(f"Failed to send video frame: {e}")

    def receive_video(self):
        try:
            compressed_frame = self.receive()
            if compressed_frame:
                frame = pickle.loads(compressed_frame)
                return frame
        except Exception as e:
            print(f"Failed to receive video frame: {e}")

    def close(self):
        if self.mode == 'client':
            self.sock.close()
        elif self.mode == 'server':
            self.conn.close()
        print("Connection closed.")
