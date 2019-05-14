from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# The vertical levels.
class Level:
    UNDEFINED = -1
    BASEMENT = 0
    FIRST_FLOOR = 1
    SECOND_FLOOR = 2
    THIRD_FLOOR = 3

from aaa_modules.layout_model.actions import turn_on_switch
reload(turn_on_switch)
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Light, Switch

from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch

# Represent a zone such as a room, foyer, porch, or lobby.
# Each zone holds a number of devices/sensors such as switches, motion sensors,
# or temperature sensor.
# Each zone instance is immutable. The various add/remove methods return a new
# Zone object. Note however that the OpenHab item underlying each
# device/sensor is not (the state changes).
#
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
#
# @Immutable (the Zone object only)
class Zone:
    # Creates a new zone.
    # @param string the zone name
    # @param devices the list of Device objects
    # @param level Level the zone's physical level
    # @param neighbors the list of optional neighbor zones.
    def __init__(self, name, devices = [], level = Level.UNDEFINED, neighbors = []):
        self.name = name
        self.level = level
        self.devices = [d for d in devices]
        self.neighbors = [n for n in neighbors]

    # Creates a new zone that is an exact copy of this one, but has the
    # additional device.
    # @return Zone A NEW object.
    def addDevice(self, device):
        if None == device:
            raise ValueError('device must not be None')

        newDevices = list(self.devices)
        newDevices.append(device)
        return Zone(self.name, newDevices, self.level, list(self.neighbors))

    # Creates a new zone that is an exact copy of this one less the given
    # device
    # @return Zone A NEW object.
    def removeDevice(self, device):
        if None == device:
            raise ValueError('device must not be None')

        newDevices = list(self.devices)
        newDevices.remove(device)
        return Zone(self.name, newDevices, self.level, list(self.neighbors))

    # Returns a copy of the list of devices.
    def getDevices(self):
        return [d for d in self.devices]

    # Returns a list of devices matching the given type.
    # @param cls Device the device type
    def getDevicesByType(self, cls):
        if None == cls:
            raise ValueError('cls must not be None')
        return [d for d in self.devices if isinstance(d, cls)]

    # Creates a new zone that is an exact copy of this one, but has the
    # additional neighbor.
    # @return Zone A NEW object.
    def addNeighbor(self, neighbor):
        if None == neighbor:
            raise ValueError('neighbor must not be None')

        newNeighbors = list(self.neighbors)
        newNeighbors.append(neighbor)

        return Zone(self.name, list(self.devices), self.level, newNeighbors)

    def getId(self):
        return str(self.getLevel()) + '_' + self.getName()

    def getName(self):
        return self.name

    def getLevel(self):
        return self.level

    # Returns a copy of the list of neighboring zones.
    def getNeighbors(self):
        return [n for n in self.neighbors]

    # Returns True if this zone contains the given itemName; returns False 
    # otherwise.
    # @param itemName string
    # @param sensorType Device an optional sub-class of Device. If specified,
    #     will search for itemName for those device types only. Otherwise,
    #     search for all devices/sensors.
    def containsOpenHabItem(self, itemName, sensorType = None):
        sensors = self.getDevices() if None == sensorType \
            else self.getDevicesByType(sensorType)
        return any(s.getItemName() == itemName for s in sensors)

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

    # Returns True if at least one light is on; returns False otherwise.
    # @return bool
    def isLightOn(self):
        return any(l.isOn() for l in self.getDevicesByType(Light))

    # Turn off all the lights in the zone.
    # @param events scope.events
    def turnOffLights(self, events):
        for l in self.getDevicesByType(Light):
            if l.isOn():
                l.turnOff(events)

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
    # @param getZoneByIdFn lambda a function that returns a Zone object given
    #     a zone id string
    # @return boolean
    # @see Switch::onSwitchTurnedOff
    def onMotionSensorTurnedOn(self, events, itemName, getZoneByIdFn):
        if not self.containsOpenHabItem(itemName, MotionSensor):
            return False 

        return TurnOnSwitch().onAction(events, self, getZoneByIdFn)

    def __str__(self):
            return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"Zone: {}, floor {}, {} devices".format(
                self.name, self.level, len(self.devices))
        for d in self.devices:
            str += u"\n  {}".format(unicode(d))

        if len(self.neighbors) > 0:
            for n in self.neighbors:
                str += u"\n  Neighbor: {}, {}".format(
                        n.getZoneId(), unicode(n.getType()))

        return str
