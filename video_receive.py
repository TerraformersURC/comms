import cv2
import numpy as np
from Comm import Comm  # Assuming Comm class is saved as comm_class.py

def receive_camera_stream(ip, port):
    # Initialize communication as server
    comm = Comm('server', ip, port)

    try:
        while True:
            # Receive frame
            frame = comm.receive_video()
            if frame is not None:
                # Display the image
                cv2.imshow('RealSense Receiver', np.array(frame, dtype=np.uint8))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cv2.destroyAllWindows()
        comm.close()

if __name__ == '__main__':
    receive_camera_stream('192.168.1.10', 12345)  # Bind to all IP addresses available on the local machine
