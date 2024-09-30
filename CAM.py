from enum import Enum
from datetime import datetime, timezone

class MessageID(Enum):
    DENM = 1  
    CAM = 2  
    POI = 3  
    SPATEM = 4  
    MAPEM = 5  
    IVIM = 6  
    EV_RSR = 7  
    TISTPGTRANSACTION = 8  
    SREM = 9  
    SSEM = 10  
    EVCSN = 11  
    SAEM = 12  
    RTCMEM = 13  

class StationType(Enum):
    UNKNOWN = 0
    PEDESTRIAN = 1
    CYCLIST = 2
    MOPED = 3
    MOTORCYCLE = 4
    PASSENGER_CAR = 5
    BUS = 6
    LIGHT_TRUCK = 7
    HEAVY_TRUCK = 8
    TRAILER = 9
    SPECIAL_VEHICLES = 10
    TRAM = 11
    ROAD_SIDE_UNIT = 15


class CAM:
    def __init__(self,header: 'ItsPduHeader', cam: 'CoopAwareness'):
        self.header = header
        self.cam = cam

class ItsPduHeader:
    def __init__(self):
        self.protocolVersion = 2
        self.messageID = MessageID.CAM

class CoopAwareness:
    def __init__(self, camParameters: 'CamParameters'):
        self.generationDeltaTime = self.generate_delta_time()
        self.camParameters = camParameters

    @staticmethod
    def generate_delta_time():
        current_time = datetime.now(timezone.utc)
        #since (2004-01-01T00:00:00:000Z)
        start_time = datetime(2004, 1, 1, tzinfo=timezone.utc)
        delta = current_time - start_time
        timestamp_its = int(delta.total_seconds() * 1000)
        # Return delta time modulo 65536
        return timestamp_its % 65536

class CamParameters:
    def __init__(
        self,
        basicContainer: 'BasicContainer',
        highFrequencyContainer: 'HighFrequencyContainer',
    ):
        self.basicContainer = basicContainer
        self.highFrequencyContainer = highFrequencyContainer

class BasicContainer:
    def __init__(self, referencePosition: 'ReferencePosition'):
        self.stationType = StationType.PASSENGER_CAR
        self.referencePosition = referencePosition

class ReferencePosition:
    def __init__(self, posx: float, posy: float):
        self.posx = posx
        self.posy = posy

class HighFrequencyContainer:
    def __init__(self, container: 'BasicVehicleContainerHighFrequency'):
        self.container = container

class BasicVehicleContainerHighFrequency:
    def __init__(
        self,
        distance:float,
        relativeSpeed: float,
        nodeId: int,
        acceleration: float,
        controllerAcceleration: float,
        speed: float        
    ):
        self.distance = distance
        self.relativeSpeed = relativeSpeed
        self.nodeId = nodeId
        self.acceleration = acceleration
        self.controllerAcceleration = controllerAcceleration
        self.speed = speed

        #Static values
        self.heading = 0 #heading car is node0
        self.leaderHeadway = 1.2
        self.leaderSpeed = 80
        self.nCars = 6
        self.nLanes = 1
        self.packetSize = 200
        self.platoonSize = 6
        self.sController = "\"CACC\""
        self.CACCspacing = 5
        self.carrierFrequency = 5.890e9
        self.car_length = 4
        self.max_deceleration = 6
        self.max_acceleration = 2.5
