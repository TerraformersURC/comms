from Comm import Comm
import pyrealsense2 as rs
import numpy as np
import cv2

# Setup RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Initialize communication
comm = Comm('192.168.1.10', 12345)  # Use the receiver's IP address and port

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
        cv2.imshow('RealSense', color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    comm.close()
