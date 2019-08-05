from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Light, Switch

from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch

from org.slf4j import Logger, LoggerFactory
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class Level:
    '''The vertical levels.'''

    UNDEFINED = -1   #: Undefined
    BASEMENT = 0     #: The basement
    FIRST_FLOOR = 1  #: The first floor
    SECOND_FLOOR = 2 #: The second floor
    THIRD_FLOOR = 3  #: The third floor

class Zone:
    """
    Represent a zone such as a room, foyer, porch, or lobby. 
    Each zone holds a number of devices/sensors such as switches, motion sensors,
    or temperature sensors.

    A zone might have zero, one or multiple adjacent zones. The adjacent zones
    can be further classified into closed space (i.e. a wall exists between the
    two zones, open space, open space slave (the neighbor is a less important
    zone), and open space master. This layout-like structure is useful for
    certain scenario such as light control.

    Each zone instance is IMMUTABLE. The various add/remove methods return a new
    Zone object. Note however that the OpenHab item underlying each
    device/sensor is not (the state changes).  See :meth:`addDevice`, 
    :meth:`removeDevice`, :meth:`addNeighbor()`

    The zone itself doesn't know how to operate a device/sensor. The sensors
    themselves (all sensors derive from Device class) exposes the possible
    operations. Generally, the zone needs not know about the exact types of 
    sensors it contains. However, controlling the light is a very common case
    for home automation; thus it does references to several virtual/physical
    sensors to determine the astro time, the illuminance, and the motion sensor.  
    See :meth:`getDevices()`, :meth:`getDevicesByType()`.

    There are two sets of operation on each zone:
      1. Active operations such as turn on a light/fan in a zone. These are\
         represented by common functions such as #turnOnLights(),\
         #turnOffLights(); and
      2. Passive operations triggered by events such onTimerExpired(),\
         onSwitchTurnedOn(), and so on.
    The passive triggering is needed because the interaction with the devices or
    sensors might happen outside the interface exposed by this class. It could
    be a manually action on the switch by the user, or a direct send command 
    through the OpenHab event bus.
    All the onXxx methods accept two parameters: the core.jsr223.scope.events
    object and the string itemName. The zone will perform appropriate actions
    for each of these events. For example, a motion event will turn on the light
    if it is dark or if it is evening time; a timer expiry event will turn off
    the associated light if it is currently on.

    @Immutable (the Zone object only)
    """

    def __init__(self, name, devices = [], level = Level.UNDEFINED, neighbors = []):
        """
        Creates a new zone.

        :param str name: the zone name
        :param list(Device) devices: the list of Device objects
        :param zone.Level level: the zone's physical level
        :param list(Neigbor) neighbors: the list of optional neighbor zones.
        """

        self.name = name
        self.level = level
        self.devices = [d for d in devices]
        self.neighbors = list(neighbors)

    def addDevice(self, device):
        '''
        Creates a new zone that is an exact copy of this one, but has the
        additional device.

        :return: A NEW object.
        :rtype: Zone
        '''
        if None == device:
            raise ValueError('device must not be None')

        newDevices = list(self.devices)
        newDevices.append(device)
        return Zone(self.name, newDevices, self.level, list(self.neighbors))

    def removeDevice(self, device):
        '''
        Creates a new zone that is an exact copy of this one less the given
        device

        :return: A NEW object.
        :rtype: Zone 
        '''
        if None == device:
            raise ValueError('device must not be None')

        newDevices = list(self.devices)
        newDevices.remove(device)
        return Zone(self.name, newDevices, self.level, list(self.neighbors))

    def getDevices(self):
        '''
        Returns a copy of the list of devices.

        :rtype: list(Device)
        '''
        return [d for d in self.devices]

    def getDevicesByType(self, cls):
        '''
        Returns a list of devices matching the given type.

        :param Device cls: the device type
        '''
        if None == cls:
            raise ValueError('cls must not be None')
        return [d for d in self.devices if isinstance(d, cls)]

    def addNeighbor(self, neighbor):
        '''
        Creates a new zone that is an exact copy of this one, but has the
        additional neighbor.

        :return: A NEW object.
        :rtype: Zone 
        '''
        if None == neighbor:
            raise ValueError('neighbor must not be None')

        newNeighbors = list(self.neighbors)
        newNeighbors.append(neighbor)

        return Zone(self.name, list(self.devices), self.level, newNeighbors)

    def getId(self):
        ''' :rtype: str '''
        return str(self.getLevel()) + '_' + self.getName()

    def getName(self):
        ''' :rtype: str '''
        return self.name

    def getLevel(self):
        ''' :rtype: zone.Level'''
        return self.level

    def getNeighbors(self):
        '''
        :return: a copy of the list of neighboring zones.
        :rtype: list(Neighbor)
        '''
        return list(self.neighbors)

    def containsOpenHabItem(self, itemName, sensorType = None):
        '''
        Returns True if this zone contains the given itemName; returns False 
        otherwise.

        :param str itemName:
        :param Device sensorType: an optional sub-class of Device. If specified,\
            will search for itemName for those device types only. Otherwise,\
            search for all devices/sensors.
        :rtype: bool
        '''
        sensors = self.getDevices() if None == sensorType \
            else self.getDevicesByType(sensorType)
        return any(s.getItemName() == itemName for s in sensors)

    def getIlluminanceLevel(self):
        '''
        Retrieves the maximum illuminance level from one or more IlluminanceSensor.
        If no sensor is available, return -1.

        :rtype: int
        '''
        illuminances = [s.getIlluminanceLevel() for s in self.getDevicesByType(
                IlluminanceSensor)]
        zoneIlluminance = -1
        if len(illuminances) > 0:
            zoneIlluminance = max(illuminances)

        return zoneIlluminance

    def isLightOnTime(self):
        '''
        Returns True if it is light-on time; returns false if it is no. Returns
        None if there is no AstroSensor to determine the time.

        :rtype: bool or None
        '''
        astroSensors = self.getDevicesByType(AstroSensor)
        if len(astroSensors) == 0:
            return None
        else:
            return any(s.isLightOnTime() for s in astroSensors)

    def isOccupied(self, minutesFromLastMotionEvent = 5):
        '''
        Returns True if the zone has at least one switch turned on, or if a
        motion event was triggered within the provided # of minutes.

        :rtype: bool
        '''
        occupied = False

        motionSensors = self.getDevicesByType(MotionSensor)
        if any(s.isOccupied(minutesFromLastMotionEvent) for s in motionSensors):
            occupied = True
        else:
            switches = self.getDevicesByType(Switch)
            if any(s.isOn() for s in switches):
                occupied = True

        return occupied

    def isLightOn(self):
        '''
        Returns True if at least one light is on; returns False otherwise.

        :rtype: bool
        '''
        return any(l.isOn() for l in self.getDevicesByType(Light))

    def shareSensorWith(self, zone, sensorType):
        '''
        Returns True if this zone shares at least one sensor of the given
        sensorType with the provider zone.
        Two sensors are considered the same if they link to the same channel.

        See :meth:`.Device.getChannel`

        :rtype: bool
        '''
        ourSensorChannels = [s.getChannel()
            for s in self.getDevicesByType(sensorType)
            if None != s.getChannel()]

        theirSensorChannels = [s.getChannel()
            for s in zone.getDevicesByType(sensorType)
            if None != s.getChannel()]

        intersection = set(ourSensorChannels).intersection(theirSensorChannels)
        return len(intersection) > 0

    def turnOffLights(self, events):
        '''
        Turn off all the lights in the zone.

        :param scope.events events:
        '''
        for l in self.getDevicesByType(Light):
            if l.isOn():
                l.turnOff(events)

    def onTimerExpired(self, events, itemName):
        '''
        Determines if the timer itemName is associated with a switch in this
        zone; if yes, turns off the switch and returns True. Otherwise returns
        False.
        '''
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.getTimerItem().getName() == itemName:
                switch.turnOff(events)
                isProcessed = True
        
        return isProcessed

    def onSwitchTurnedOn(self, events, itemName, getZoneByIdFn):
        '''
        If itemName belongs to this zone, dispatches the event to the associated
        Switch object, and returns True. Otherwise return False.

        See :meth:`.Switch.onSwitchTurnedOn`

        :param lambda getZoneByIdFn: a function that returns a Zone object \
            given a zone id string
        :rtype: boolean
        '''
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOn(events, itemName):
                TurnOffAdjacentZones().onAction(events, self, getZoneByIdFn)
                isProcessed = True
        
        return isProcessed

    def onSwitchTurnedOff(self, events, itemName):
        '''
        If itemName belongs to this zone, dispatches the event to the associated
        Switch object, and returns True. Otherwise return False.

        See :meth:`.Switch.onSwitchTurnedOff`

        :rtype: boolean
        '''
        isProcessed = False

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOff(events, itemName):
                isProcessed = True
        
        return isProcessed

    def onMotionSensorTurnedOn(self, events, itemName, getZoneByIdFn):
        '''
        If the motion sensor belongs to this zone, turns on the associated
        switch, and returns True. Otherwise return False.

        :param lambda getZoneByIdFn: a function that returns a Zone object\
            given a zone id string
        :rtype: boolean
        '''
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
