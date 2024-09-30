import socket
import json
import time
import threading
from CAM import CAM, ItsPduHeader, CoopAwareness, CamParameters, BasicContainer, ReferencePosition, HighFrequencyContainer, BasicVehicleContainerHighFrequency

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
    try:
        lines = [float(file.readline().strip()) for _ in range(8)]
        return lines if len(lines) == 8 else None
    except ValueError:
        return None

def send_cam(data, ip_address, port=37020):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.sendto(data.encode('utf-8'), (ip_address, port))
    except Exception as e:
        print(f"Error sending CAM message: {e}")

def send_cam_messages(cam, file, ip_address, stop_event):
    while not stop_event.is_set():
        # Read the next 8 lines of data from the file
        data = read_data_from_file(file)
        if data is None:
            print("End of file reached or invalid data.")
            break

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

        time.sleep(0.1)

def print_cam_data(cam_data):
    try:
        cam_parameters = cam_data['cam']['camParameters']
        high_freq = cam_parameters['highFrequencyContainer']
        basic_container = cam_parameters['basicContainer']
        
        print(f"Distance: {high_freq['distance']}")
        print(f"Relative Speed: {high_freq['relativeSpeed']}")
        print(f"Node ID: {high_freq['nodeId']}")
        print(f"Acceleration: {high_freq['acceleration']}")
        print(f"Controller Acceleration: {high_freq['controllerAcceleration']}")
        print(f"Speed: {high_freq['speed']}")
        print(f"Position X: {basic_container['referencePosition']['posx']}")
        print(f"Position Y: {basic_container['referencePosition']['posy']}")
        print("-" * 50)
    except KeyError as e:
        print(f"Error parsing CAM data: missing {e}")

def receive_cam_messages(stop_event):
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 37020))  # Listen on all interfaces, port 37020
        udp_socket.settimeout(1)  # Add timeout to allow thread to exit gracefully

        print("Listening for CAM messages...")

        while not stop_event.is_set():
            try:
                data, addr = udp_socket.recvfrom(1024)
                cam_data = json.loads(data.decode('utf-8'))

                received_node_id = cam_data['cam']['camParameters']['highFrequencyContainer']['nodeId']
                if received_node_id == 0:  # Filter out own messages
                    continue

                print(f"Received CAM message from {addr}")
                print_cam_data(cam_data)
            except socket.timeout:
                continue  # Allow thread to exit on timeout
            except json.JSONDecodeError:
                print("Error decoding CAM message")
    except Exception as e:
        print(f"Error receiving CAM messages: {e}")
    finally:
        udp_socket.close()

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

    broadcast_ip = '10.15.4.255'  # Broadcast address
    file_path = '0.txt'  # File containing data to send

    # Stop event to control threads
    stop_event = threading.Event()

    try:
        # Open the data file
        with open(file_path, 'r') as file:
            # Create threads for sending and receiving CAM messages
            send_thread = threading.Thread(target=send_cam_messages, args=(cam_message, file, broadcast_ip, stop_event))
            receive_thread = threading.Thread(target=receive_cam_messages, args=(stop_event,))

            # Start threads
            send_thread.start()
            receive_thread.start()

            # Wait for threads to finish
            send_thread.join()
            stop_event.set()  # Signal receive thread to stop
            receive_thread.join()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except KeyboardInterrupt:
        print("Program interrupted by user.")
        stop_event.set()  # Signal threads to stop

if __name__ == "__main__":
    main()
