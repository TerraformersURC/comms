import sys
import threading
import socket
import numpy
import base64
import time
from datetime import datetime
import cv2
import pyrealsense2 as rs

class ServerSocket:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
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
        cnt = 0
        try:
            while True:
                lengthcolor = (self.recvall(self.conn, 64)).decode('utf-8')
                stringcolor = self.recvall(self.conn, int(lengthcolor))
                lengthdepth = (self.recvall(self.conn, 64)).decode('utf-8')
                stringdepth = self.recvall(self.conn, int(lengthdepth))
                stime = self.recvall(self.conn, 64)
                print('send time: ' + stime.decode('utf-8'))
                now = time.localtime()
                print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                
                colordata = numpy.frombuffer(base64.b64decode(stringcolor), numpy.uint8)
                deccolor = cv2.imdecode(colordata, 1)
                depthdata = numpy.frombuffer(base64.b64decode(stringdepth), numpy.uint8)
                decdepth = cv2.imdecode(depthdata, 1)
                cv2.imshow('RealSense', numpy.hstack((deccolor, decdepth)))
                cv2.waitKey(1)

        except Exception as e:
            print(e)
            self.socketClose()
            cv2.destroyAllWindows()
            self.socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def main():
    if len(sys.argv) != 3:
        print("Usage: python ServerSocket.py <TCP_IP> <TCP_PORT>")
        sys.exit(1)

    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])

    server = ServerSocket(TCP_IP, TCP_PORT)

if __name__ == "__main__":
    main()
