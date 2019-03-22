from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# The vertical levels.
class Level:
    UNDEFINED = 0
    FIRST_FLOOR = 1
    SECOND_FLOOR = 2
    THIRD_FLOOR = 3
    BASEMENT = 4

#from aaa_modules.layout_model import switch
#reload(switch)
from aaa_modules.layout_model.switch import Switch

# Represent a zone such as a room, foyer, porch, or lobby.
class Zone:
    def __init__(self, name, devices = [], level = Level.UNDEFINED):
        self.name = name
        self.level = level
        self.devices = devices

    def addDevice(self, device):
        if None == device:
            raise ValueError('device must not be None')
        self.devices.append(device)

    def removeDevice(self, device):
        if None == device:
            raise ValueError('device must not be None')
        self.devices.remove(device)

    def getDevices(self):
        return [d for d in self.devices]

    def getDevicesByType(self, cls):
        if None == cls:
            raise ValueError('cls must not be None')
        return [d for d in self.devices if isinstance(d, cls)]

    def getName(self):
        return self.name

    def getLevel(self):
        return self.level

    # Returns true if the zone has at least one switch turned on, or if a
    # motion event was triggered within the provided # of minutes.
    def isOccupied(self, minutesFromLastMotionEvent = 5):
        pass

    def onTimerExpired(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.getTimerItem().getName() == itemName:
                switch.turnOff(events)
                isProcessed = True
        
        return isProcessed

    def onSwitchTurnedOn(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOn(events, itemName):
                isProcessed = True
        
        return isProcessed

    def onSwitchTurnedOff(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOff(events, itemName):
                isProcessed = True
        
        return isProcessed

