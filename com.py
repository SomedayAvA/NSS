import socket
import json
import time
import threading
from CAM import CAM, ItsPduHeader, CoopAwareness, CamParameters, BasicContainer, ReferencePosition, HighFrequencyContainer, BasicVehicleContainerHighFrequency
node_id = 0  
UDP_PORT = 37020
CAM_INTERVAL = 0.1 
def serialize_cam(cam):
    return json.dumps({
        'header': {
            'protocolVersion': cam.header.protocolVersion,
            'messageID': cam.header.messageID.name
        },
        'cam': {
            'generationDeltaTime': cam.cam.generationDeltaTime,
            'camParameters': {
                'basicContainer': {
                    'stationType': cam.cam.camParameters.basicContainer.stationType.name,
                    'referencePosition': {
                        'posx': cam.cam.camParameters.basicContainer.referencePosition.posx,
                        'posy': cam.cam.camParameters.basicContainer.referencePosition.posy
                    }
                },
                'highFrequencyContainer': {
                    'distance': cam.cam.camParameters.highFrequencyContainer.container.distance,
                    'relativeSpeed': cam.cam.camParameters.highFrequencyContainer.container.relativeSpeed,
                    'nodeId': cam.cam.camParameters.highFrequencyContainer.container.nodeId,
                    'acceleration': cam.cam.camParameters.highFrequencyContainer.container.acceleration,
                    'controllerAcceleration': cam.cam.camParameters.highFrequencyContainer.container.controllerAcceleration,
                    'speed': cam.cam.camParameters.highFrequencyContainer.container.speed
                }
            }
        }
    })


def read_data_from_file(file):
    lines = []
    for _ in range(8):
        line = file.readline().strip()
        if not line:  # If the file ends before 8 lines
            return None  # Return None to stop the process
        lines.append(float(line))
    return lines

def send_cam(data, ip_address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    udp_socket.sendto(data.encode('utf-8'), (ip_address, UDP_PORT))


def send_cam_messages(cam, file, ip_address):
    while True:
        # Read the next 8 lines of data from the file
        data = read_data_from_file(file)
        
        if data is None:
            print("End of file reached.")
            break  # Stop the process when no more data is available

        cam.cam.camParameters.highFrequencyContainer.container.distance = data[0]
        cam.cam.camParameters.highFrequencyContainer.container.relativeSpeed = data[1]
        cam.cam.camParameters.highFrequencyContainer.container.nodeId = int(data[2])
        cam.cam.camParameters.highFrequencyContainer.container.acceleration = data[3]
        cam.cam.camParameters.highFrequencyContainer.container.controllerAcceleration = data[4]
        cam.cam.camParameters.highFrequencyContainer.container.speed = data[5]
        cam.cam.camParameters.basicContainer.referencePosition.posx = data[6]
        cam.cam.camParameters.basicContainer.referencePosition.posy = data[7]

        cam.cam.generationDeltaTime = cam.cam.generate_delta_time()

        cam_data = serialize_cam(cam)

        send_cam(cam_data, ip_address)
        
        time.sleep(CAM_INTERVAL)

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

    basic_container = cam_parameters['basicContainer']
    posx = basic_container['referencePosition']['posx']
    posy = basic_container['referencePosition']['posy']
    
    print(f"Distance: {distance}")
    print(f"Relative Speed: {relative_speed}")
    print(f"Node ID: {node_id}")
    print(f"Acceleration: {acceleration}")
    print(f"Controller Acceleration: {controller_acceleration}")
    print(f"Speed: {speed}")
    print(f"Position X: {posx}")
    print(f"Position Y: {posy}")
    print("-" * 50)

# Function to receive CAM messages via UDP and print them
def receive_cam_messages():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', UDP_PORT))  

    print("Listening for CAM messages...")

    while True:
        data, addr = udp_socket.recvfrom(1024) 
        cam_data = json.loads(data.decode('utf-8')) 


        received_node_id = cam_data['cam']['camParameters']['highFrequencyContainer']['nodeId']

  
        if received_node_id == node_id:
            continue

        print(f"Received CAM message from {addr}")
        print_cam_data(cam_data)


# Main function to run the send and receive threads
def main():
    reference_position = ReferencePosition(posx=100.0, posy=200.0)
    basic_container = BasicContainer(referencePosition=reference_position)
    high_freq_container = HighFrequencyContainer(
        BasicVehicleContainerHighFrequency(
            distance=10.5, relativeSpeed=1.2, nodeId=1, acceleration=2.0, controllerAcceleration=1.5, speed=60.0
        )
    )
    cam_params = CamParameters(basic_container, high_freq_container)
    cam_message = CAM(ItsPduHeader(), CoopAwareness(cam_params))

  
    broadcast_ip = '10.0.0.255'

   
    file = open(f'{node_id}.txt', 'r')

    send_thread = threading.Thread(target=send_cam_messages, args=(cam_message, file, broadcast_ip))

   
    receive_thread = threading.Thread(target=receive_cam_messages)

  
    send_thread.start()
    receive_thread.start()

  
    send_thread.join()
    receive_thread.join()


# Run the program
if __name__ == "__main__":
    main()
