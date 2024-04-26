import sys
import threading
import socket
import numpy
import base64
import time
from datetime import datetime
import cv2
import pyrealsense2 as rs

class ClientSocket:
    def __init__(self, ip, port):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.connectServer()

    def connectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            self.sendImages()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(u'Connect fail %d times. exit program'%(self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server'%(self.connectCount))
            self.connectServer()

    def sendImages(self):
        cnt = 0
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        try:
            pipeline.start(config)
            while True:
                frames = pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()
                frame = numpy.asanyarray(color_frame.get_data())

                resize_frame = cv2.resize(frame, dsize=(480, 315), interpolation=cv2.INTER_AREA)
                
                #now = time.localtime()
                stime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                result, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
                data = numpy.array(imgencode)
                stringData = base64.b64encode(data)
                length = str(len(stringData))
                print(length)
                self.sock.sendall(length.encode('utf-8').ljust(64))
                self.sock.send(stringData)
                self.sock.send(stime.encode('utf-8').ljust(64))
                print(u'send images %d'%(cnt))
                cnt+=1
                time.sleep(.095)

        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.connectServer()
            self.sendImages()

def main():
    if len(sys.argv) != 3:
        print("Usage: python ClientSocket.py <TCP_IP> <TCP_PORT>")
        sys.exit(1)

    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])

    client = ClientSocket(TCP_IP, TCP_PORT)

if __name__ == "__main__":
    main()
