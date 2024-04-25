from Comm import Comm
import cv2
import numpy as np
import pyrealsense2 as rs

# Create a pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the camera
pipeline.start(config)

# Initialize communication
comm = Comm('192.168.1.10', 12345)

try:
    while True:
        # Send video frame
        comm.send_video(pipeline)

        # Receive video frame
        comm.receive_video()
finally:
    # Stop streaming
    pipeline.stop()