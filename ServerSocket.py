import sys
import threading
import socket
import numpy
import base64
import time
import datetime
import cv2
import pyrealsense2 as rs

class ServerSocket:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is closed')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

    def receiveImages(self):

        try:
            while True:
                frames = self.pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                frame = numpy.asanyarray(color_frame.get_data())

                now = time.localtime()
                stime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                data = numpy.array(imgencode)
                stringData = base64.b64encode(data)
                length = str(len(stringData))
                self.conn.sendall(length.encode('utf-8').ljust(64))
                self.conn.send(stringData)
                self.conn.send(stime.encode('utf-8').ljust(64))
                print(u'send images')
                time.sleep(0.095)
        except Exception as e:
            print(e)
            self.socketClose()
            self.socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

def main():
    if len(sys.argv) != 3:
        print("Usage: python ServerSocket.py <TCP_IP> <TCP_PORT>")
        sys.exit(1)

    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])

    server = ServerSocket(TCP_IP, TCP_PORT)

if __name__ == "__main__":
    main()
