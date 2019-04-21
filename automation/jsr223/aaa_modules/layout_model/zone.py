from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# The vertical levels.
class Level:
    UNDEFINED = -1
    BASEMENT = 0
    FIRST_FLOOR = 1
    SECOND_FLOOR = 2
    THIRD_FLOOR = 3

from aaa_modules.layout_model import switch
reload(switch)
from aaa_modules.layout_model import astro_sensor
reload(astro_sensor)
from aaa_modules.layout_model import illuminance_sensor
reload(illuminance_sensor)
from aaa_modules.layout_model import motion_sensor
reload(motion_sensor)
from aaa_modules.layout_model import dimmer
reload(dimmer)
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Light, Switch

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
# All the onXxx methods accept two parameters: the core.jsr223.scope.events
# object and the string itemName. The zone will perform appropriate actions
# for each of these events. For example, a motion event will turn on the light
# if it is dark or if it is evening time; a timer expiry event will turn off
# the associated light if it is currently on.
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

    # Retrieves the maximum illuminance level from one or more IlluminanceSensor.
    # If no sensor is available, return -1.
    # @return int
    def getIlluminanceLevel(self):
        illuminances = [s.getIlluminanceLevel() for s in self.getDevicesByType(
                IlluminanceSensor)]
        zoneIlluminance = -1
        if len(illuminances) > 0:
            zoneIlluminance = max(illuminances)

        return zoneIlluminance

    # Returns True if it is light-on time; returns false if it is no. Returns
    # None if there is no AstroSensor to determine the time.
    # @return bool or None
    def isLightOnTime(self):
        astroSensors = self.getDevicesByType(AstroSensor)
        if len(astroSensors) == 0:
            return None
        else:
            return any(s.isLightOnTime() for s in astroSensors)

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
        motionSensors = self.getDevicesByType(MotionSensor)
        if not any(s.onMotionSensorTurnedOn(events, itemName) for s in motionSensors):
            return False

        isProcessed = False
        lightOnTime = self.isLightOnTime()
        zoneIlluminance = self.getIlluminanceLevel()

        for switch in self.getDevicesByType(Switch):
            if isinstance(switch, Light):
                if (lightOnTime or
                        None == switch.getIlluminanceThreshold() or 
                        zoneIlluminance < switch.getIlluminanceThreshold()):
                    switch.turnOn(events)
                    isProcessed = True
            else:
                switch.turnOn(events)
                isProcessed = True
        
        return isProcessed

    def __str__(self):
            return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"Zone: {}, floor {}, {} devices".format(
                self.name, self.level, len(self.devices))
        for d in self.devices:
            str += u"\n  {}".format(unicode(d))

        return str
