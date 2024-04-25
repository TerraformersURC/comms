import pyrealsense2 as rs
import numpy as np
import cv2
from Comm import Comm  # Assuming Comm class is saved as comm_class.py

def start_camera_stream(ip, port):
    # Setup RealSense
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    # Initialize communication as client
    comm = Comm('client', ip, port)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert image to numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Send the frame
            comm.send_video(color_image)

            # Display the image locally
            cv2.imshow('RealSense Sender', color_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        comm.close()

if __name__ == '__main__':
    start_camera_stream('192.168.1.10', 12345)  # Enter the receiver's IP and the port number
