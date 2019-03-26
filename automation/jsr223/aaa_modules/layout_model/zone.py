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
from aaa_modules.layout_model.motion_sensor import MotionSensor

# Represent a zone such as a room, foyer, porch, or lobby.
# Each zone holds a number of devices/sensors such as switches, motion sensors,
# or temperature sensor.
# There are two sets of operation on each zone:
#   1. Active operations such as turn on a light/fan in a zone. These are
#      represented by functions such as turnOnLight(), turnOffLight(); and
#   2. Passive operations triggered by events such onTimerExpired(),
#      onSwitchTurnedOn(), and so on.
# The passive triggering is needed because the interaction with the devices or
# sensors might happen outside the interface exposed by this class. It could
# be a manually action on the switch by the user, or a direct send command 
# through the OpenHab event bus.
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

    # Returns True if the zone has at least one switch turned on, or if a
    # motion event was triggered within the provided # of minutes.
    # @return bool
    def isOccupied(self, minutesFromLastMotionEvent = 5):
        occupied = False

        motionSensors = self.getDevicesByType(MotionSensor)
        if any(s.isOccupied(minutesFromLastMotionEvent) for s in motionSensors):
            occupied = True
        else:
            switches = self.getDevicesByType(Switch)
            if any(s.isOn() for s in switches):
                occupied = True

        return occupied

    # Determines if the timer itemName is associated with a switch in this
    # zone; if yes, turns off the switch and returns True. Otherwise returns
    # False.
    def onTimerExpired(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.getTimerItem().getName() == itemName:
                switch.turnOff(events)
                isProcessed = True
        
        return isProcessed

    # If itemName belongs to this zone, dispatches the event to the associated
    # Switch object, and returns True. Otherwise return False.
    # @return boolean
    # @see Switch::onSwitchTurnedOn
    def onSwitchTurnedOn(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOn(events, itemName):
                isProcessed = True
        
        return isProcessed

    # If itemName belongs to this zone, dispatches the event to the associated
    # Switch object, and returns True. Otherwise return False.
    # @return boolean
    # @see Switch::onSwitchTurnedOff
    def onSwitchTurnedOff(self, events, itemName):
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOff(events, itemName):
                isProcessed = True
        
        return isProcessed

    # If the motion sensor belongs to this zone, turns on the associated
    # switch, and returns True. Otherwise return False.
    # @return boolean
    # @see Switch::onSwitchTurnedOff
    def onMotionSensorTurnedOn(self, events, itemName):
        isProcessed = False

        sensors = self.getDevicesByType(MotionSensor)
        if any(s.onMotionSensorTurnedOn(events, itemName) for s in sensors):
            for switch in self.getDevicesByType(Switch):
                switch.turnOn(events)

            isProcessed = True
        
        return isProcessed

