import sys
import threading
import socket
import numpy
import base64
import time
from datetime import datetime
import pyrealsense2 as rs
import argparse
import cv2
import math


class ClientSocket:
    def __init__(self, ip, port):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        #self.connectServer()
        self.sendImages()

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
                print(u'Connect fail %d times. exit program' % (self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server' % (self.connectCount))
            self.connectServer()

    def sendImages(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-t", "--type", type=str,
                        default="DICT_ARUCO_ORIGINAL",
                        help="type of ArUCo tag to detect")
        args = vars(ap.parse_args())

        with numpy.load('camera_calibration_parameters.npz') as data:
            camera_matrix = data['camera_matrix']
            dist_coeffs = data['dist_coeffs']

        # Define the actual size of the AprilTag in meters
        tag_size = 0.1  # Example: 10 cm

        # Extract the focal length (fx) from the camera matrix
        focal_length = camera_matrix[0, 0]  # fx from the intrinsic matrix

        ARUCO_DICT = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
            "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
            "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
            "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
        }

        # Verify that the supplied ArUCo tag exists and is supported by OpenCV
        if ARUCO_DICT.get(args["type"], None) is None:
            print("[INFO] ArUCo tag of '{}' is not supported".format(args["type"]))
            sys.exit(0)

        # Load the ArUCo dictionary and grab the ArUCo parameters
        print("[INFO] detecting '{}' tags...".format(args["type"]))
        arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_7X7_100)
        arucoParams = cv2.aruco.DetectorParameters()

        # Initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        cnt = 0
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

        try:
            pipeline.start(config)
            while True:
                frames = pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                if not depth_frame or not color_frame:
                    continue

                stime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                color_image = numpy.asanyarray(color_frame.get_data())

                resize_color = cv2.resize(color_image, dsize=(480, 315), interpolation=cv2.INTER_AREA)
                result, colorencode = cv2.imencode('.jpg', resize_color, encode_param)
                colordata = numpy.array(colorencode)
                stringcolor = base64.b64encode(colordata)
                lengthcolor = str(len(stringcolor))
                print("color length: " + lengthcolor)

                depth_image = numpy.asanyarray(depth_frame.get_data())
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                resize_depth = cv2.resize(depth_colormap, dsize=(480, 315), interpolation=cv2.INTER_AREA)
                _, depthencode = cv2.imencode('.jpg', resize_depth, encode_param)
                depthdata = numpy.array(depthencode)
                stringdepth = base64.b64encode(depthdata)
                lengthdepth = str(len(stringdepth))
                print("depth length: " + lengthdepth)
                if cnt == 10:
                    cv2.imwrite('testing/original_depth1.jpg', cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET))

                detector = cv2.aruco.ArucoDetector(arucoDict, arucoParams)
                (corners, ids, rejected) = detector.detectMarkers(color_image)

                # Verify at least one ArUco marker was detected
                if len(corners) > 0:
                    # Flatten the ArUco IDs list
                    ids = ids.flatten()
                    # Loop over the detected ArUCo corners
                    for (markerCorner, markerID) in zip(corners, ids):
                        # Extract the marker corners (which are always returned
                        # in top-left, top-right, bottom-right, and bottom-left order)
                        corners = markerCorner.reshape((4, 2))
                        print(corners)

                        tag_pixel_size = (numpy.linalg.norm(corners[0] - corners[1]) +
                                          numpy.linalg.norm(corners[1] - corners[2]) +
                                          numpy.linalg.norm(corners[2] - corners[3]) +
                                          numpy.linalg.norm(corners[3] - corners[0])) / 4

                        # Calculate the distance using the pixel size and convert to millimeters
                        distance_pixel_method = (tag_size * focal_length) / tag_pixel_size * 1000

                        # Define the 3D coordinates of the tag's corners in the tag's coordinate frame
                        obj_points = numpy.array([[-tag_size / 2, tag_size / 2, 0],
                                                [tag_size / 2, tag_size / 2, 0],
                                                [tag_size / 2, -tag_size / 2, 0],
                                                [-tag_size / 2, -tag_size / 2, 0]], dtype=numpy.float32)

                        # Estimate the pose of the tag
                        retval, rvec, tvec = cv2.solvePnP(obj_points, corners, camera_matrix, dist_coeffs)

                        if retval:
                            # Draw the detected tag corners on the frame
                            for i in range(4):
                                pt1 = tuple(map(int, corners[i]))
                                pt2 = tuple(map(int, corners[(i + 1) % 4]))
                                cv2.line(color_image, pt1, pt2, (0, 255, 0), 2)

                            # Convert rotation vector to rotation matrix
                            rot_matrix, _ = cv2.Rodrigues(rvec)

                            # Calculate yaw, pitch, and roll from the rotation matrix
                            sy = numpy.sqrt(rot_matrix[0, 0] ** 2 + rot_matrix[1, 0] ** 2)
                            singular = sy < 1e-6
                            if not singular:
                                yaw = numpy.arctan2(rot_matrix[2, 1], rot_matrix[2, 2])
                                pitch = numpy.arctan2(-rot_matrix[2, 0], sy)
                                roll = numpy.arctan2(rot_matrix[1, 0], rot_matrix[0, 0])
                            else:
                                yaw = numpy.arctan2(-rot_matrix[1, 2], rot_matrix[1, 1])
                                pitch = numpy.arctan2(-rot_matrix[2, 0], sy)
                                roll = 0

                            # Convert angles to degrees
                            yaw, pitch, roll = numpy.degrees([yaw, pitch, roll])

                            # Calculate the distance using the translation vector and convert to millimeters
                            distance_tvec = numpy.linalg.norm(tvec) * 1000  # Convert to mm

                            # Display the tag's information on the frame
                            tag_id = markerID
                            text = f'ID: {tag_id}, Dist: {distance_tvec:.1f} mm, Pixel Dist: {distance_pixel_method:.1f} mm'
                            text2 = f'Yaw: {yaw:.1f}, Pitch: {pitch:.1f}, Roll: {roll:.1f}'
                            cv2.putText(color_image, text, (pt1[0], pt1[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                            cv2.putText(color_image, text2, (pt1[0], pt1[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                            # Draw the coordinate axes on the tag
                            cv2.drawFrameAxes(color_image, camera_matrix, dist_coeffs, rvec, tvec, 0.05)

                            # Print the position and distances
                            print(f"Tag ID: {tag_id} - Position (x, y, z): {tvec.flatten()} - Distance (mm): {distance_tvec:.1f}")

                # Display the frame with detected markers and distance information
                cv2.imshow("ArUco Marker Detection", color_image)

                # Break the loop if the user presses 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                """
                self.sock.sendall(lengthcolor.encode('utf-8').ljust(64))
                self.sock.send(stringcolor)
                self.sock.sendall(lengthdepth.encode('utf-8').ljust(64))
                self.sock.send(stringdepth)
                self.sock.send(stime.encode('utf-8').ljust(64))
                print(u'send images %d' % (cnt))
                cnt += 1
                """
                time.sleep(.095)

        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.connectServer()
            self.sendImages()


def main():
    TCP_IP = '127.0.0.1'
    TCP_PORT = 8000

    client = ClientSocket(TCP_IP, TCP_PORT)


if __name__ == "__main__":
    main()

