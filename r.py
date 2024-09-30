import socket
import json

# Function to parse and print the relevant fields from the CAM message
def print_cam_data(cam_data):
    cam_parameters = cam_data['cam']['camParameters']
    
    # Extracting the high frequency container values
    high_freq = cam_parameters['highFrequencyContainer']
    distance = high_freq['distance']
    relative_speed = high_freq['relativeSpeed']
    node_id = high_freq['nodeId']
    acceleration = high_freq['acceleration']
    controller_acceleration = high_freq['controllerAcceleration']
    speed = high_freq['speed']

    # Extracting the basic container reference position
    basic_container = cam_parameters['basicContainer']
    posx = basic_container['referencePosition']['posx']
    posy = basic_container['referencePosition']['posy']
    
    # Print the extracted data
    print(f"Distance: {distance}")
    print(f"Relative Speed: {relative_speed}")
    print(f"Node ID: {node_id}")
    print(f"Acceleration: {acceleration}")
    print(f"Controller Acceleration: {controller_acceleration}")
    print(f"Speed: {speed}")
    print(f"Position X: {posx}")
    print(f"Position Y: {posy}")
    print("-" * 50)

# Listening for incoming UDP packets
def receive_cam_messages():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 37020))  # Bind to all available interfaces and port 37020

    print("Listening for CAM messages...")

    while True:
        data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
        cam_data = json.loads(data.decode('utf-8'))  # Parse the received JSON data

        print(f"Received CAM message from {addr}")
        print_cam_data(cam_data)

# Run the receiver
receive_cam_messages()
