# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import smbus
import time
import socket
import json

""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080 displayd in a 1/4 size window
"""

# Constants for the ICM-20948
I2C_ADDRESS = 0x68
WHO_AM_I = 0x00
PWR_MGMT_1 = 0x06
PWR_MGMT_2 = 0x07
ACCEL_XOUT_H = 0x2D
ACCEL_XOUT_L = 0x2E
ACCEL_YOUT_H = 0x2F
ACCEL_YOUT_L = 0x30
ACCEL_ZOUT_H = 0x31
ACCEL_ZOUT_L = 0x32
GYRO_XOUT_H = 0x37
GYRO_XOUT_L = 0x38
TEMP_OUT = 0x39
ACCEL_CONFIG = 0x14

# Initialize the I2C bus
bus = smbus.SMBus(1)

# Verify the device ID
device_id = bus.read_byte_data(I2C_ADDRESS, WHO_AM_I)
print(f"Device ID: {device_id:#x}")

# Wake the device and select the best clock source
bus.write_byte_data(I2C_ADDRESS, PWR_MGMT_1, 0x01)

# Enable accelerometer and gyroscope (all axes)
bus.write_byte_data(I2C_ADDRESS, PWR_MGMT_2, 0x00)

bus.write_byte_data(I2C_ADDRESS, ACCEL_CONFIG, 0x18)

sensitivity = 1/2048.0

def read_acceleration(L, H):
    # Read the high and low parts of the X acceleration
    high = bus.read_byte_data(I2C_ADDRESS, H)
    low = bus.read_byte_data(I2C_ADDRESS, L)
    # Combine the two bytes and convert to a signed number
    value = (high << 8) | low
    if value >= 0x8000:
        value -= 0x10000
    return value * sensitivity

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )












# Sending IMU data from Jetson to Xcode

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_address = ('10.4.16.141', 55000)
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

print("Waiting for a connection...")
connection, client_address = server_socket.accept()
print("Connection from:", client_address)

try:
    while True:
        # Read IMU sensor data
        # ...

        # Create a JSON object with IMU data
        imu_data = {
            "x_accel": read_acceleration(ACCEL_XOUT_L, ACCEL_XOUT_H),
            "y_accel": read_acceleration(ACCEL_YOUT_L, ACCEL_YOUT_H),
            "z_accel": read_acceleration(ACCEL_ZOUT_L, ACCEL_ZOUT_H) - 8
        }
        print(read_acceleration(ACCEL_XOUT_L, ACCEL_XOUT_H))
        print(imu_data)
        # Send IMU data over the socket
        try:
            connection.sendall(json.dumps(imu_data).encode('utf-8'))
        except socket.error as e:
            print(f"Socket error: {e}")
            break

finally:
    # Clean up the connection
    connection.close()














# Camera

def show_camera():
    window_title = "CSI Camera"

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    print(gstreamer_pipeline(flip_method=0))
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    if video_capture.isOpened():
        try:
            window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            while True:
                ret_val, frame = video_capture.read()
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, frame)
                else:
                    break 
                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")
def picture_time():
    cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

    cv2.namedWindow("test")

    img_counter = 0

    while True:
        x_accel = read_acceleration(ACCEL_XOUT_L, ACCEL_XOUT_H)
        #print(f"X-Acceleration: {x_accel}")
        y_accel = read_acceleration(ACCEL_YOUT_L, ACCEL_YOUT_H)
        #print(f"Y-Acceleration: {y_accel}")
        z_accel = read_acceleration(ACCEL_ZOUT_L, ACCEL_ZOUT_H) - 8
        #print(f"Z-Acceleration: {z_accel}")
        #time.sleep(1)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "opencv_frame_{}.png".format(img_counter)
            if(x_accel < 0.8 and x_accel > -0.8 and y_accel < 0.8 and y_accel > -0.8 and z_accel < 0.8 and z_accel > -0.8):
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
                time.sleep(5)
    cam.release()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    picture_time()
