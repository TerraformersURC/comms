from Comm import Comm
import cv2

# Initialize communication
comm = Comm('192.168.1.10', 12345)  # Bind to all IP addresses available on the local machine

try:
    while True:
        # Receive frame
        frame = comm.receive_video()
        if frame is not None:
            # Display the image
            cv2.imshow('Received RealSense Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
finally:
    cv2.destroyAllWindows()
    comm.close()
