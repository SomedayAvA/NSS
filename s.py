import socket
import json
import time

# Function to serialize the CAM object to JSON
def serialize_cam(cam: CAM):
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

# Function to read 8 lines from the file and update the CAM object
def read_data_from_file(file):
    lines = []
    for _ in range(8):
        line = file.readline().strip()
        if not line:  # If the file ends before 8 lines
            return None  # Return None to stop the process
        lines.append(float(line))
    return lines

# Function to send CAM message via UDP (unicast)
def send_cam(data, ip_address):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(data.encode('utf-8'), (ip_address, 37020))  # Change IP address to unicast

# Create the initial CAM object
reference_position = ReferencePosition(posx=100.0, posy=200.0)
basic_container = BasicContainer(referencePosition=reference_position)
high_freq_container = HighFrequencyContainer(
    BasicVehicleContainerHighFrequency(
        distance=10.5, relativeSpeed=1.2, nodeId=1, acceleration=2.0, controllerAcceleration=1.5, speed=60.0
    )
)
cam_params = CamParameters(basic_container, high_freq_container)
cam_message = CAM(ItsPduHeader(), CoopAwareness(cam_params))

# Define the IP address for unicast
unicast_ip = '192.168.1.100'  # Replace with the target device's IP address

# Open the file containing the data
with open('data.txt', 'r') as file:
    while True:
        # Read the next 8 lines of data from the file
        data = read_data_from_file(file)
        
        if data is None:
            print("End of file reached.")
            break  # Stop the process when no more data is available

        # Update the CAM object with the new data
        high_freq_container.container.distance = data[0]
        high_freq_container.container.relativeSpeed = data[1]
        high_freq_container.container.nodeId = int(data[2])
        high_freq_container.container.acceleration = data[3]
        high_freq_container.container.controllerAcceleration = data[4]
        high_freq_container.container.speed = data[5]
        basic_container.referencePosition.posx = data[6]
        basic_container.referencePosition.posy = data[7]

        # Update CAM generationDeltaTime
        cam_message.cam.generationDeltaTime = cam_message.cam.generate_delta_time()

        # Serialize CAM to JSON format
        cam_data = serialize_cam(cam_message)

        # Send the serialized CAM message via unicast
        send_cam(cam_data, unicast_ip)
        
        print(f"Sending CAM to {unicast_ip}:", cam_data)
        
        # Wait for 0.1 seconds before sending the next message
        time.sleep(0.1)
