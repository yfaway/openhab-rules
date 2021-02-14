from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.device import Device

from aaa_modules.layout_model.devices.astro_sensor import AstroSensor
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.switch import Light, Switch

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class Level:
    ''' An enum of the vertical levels.'''

    UNDEFINED = -1   #: Undefined
    BASEMENT = 0     #: The basement
    FIRST_FLOOR = 1  #: The first floor
    SECOND_FLOOR = 2 #: The second floor
    THIRD_FLOOR = 3  #: The third floor

class ZoneEvent:
    ''' An enum of triggering zone events. '''

    UNDEFINED = -1                   # Undefined
    MOTION = 1                       # A motion triggered event
    SWITCH_TURNED_ON = 2             # A switch turned-on event
    SWITCH_TURNED_OFF = 3            # A switch turned-on event
    CONTACT_OPEN = 4                 # A contact (doors/windows) is open
    CONTACT_CLOSED = 5               # A contact (doors/windows) is close
    PARTITION_ARMED_AWAY = 6         # Changed to armed away
    PARTITION_ARMED_STAY = 7         # Changed to armed stay
    PARTITION_DISARMED_FROM_AWAY = 8 # Changed from armed away to disarm
    PARTITION_DISARMED_FROM_STAY = 9 # Changed from armed stay to disarm
    HUMIDITY_CHANGED = 10            # The humidity percentage changed
    TEMPERATURE_CHANGED = 11         # The temperature changed
    GAS_TRIGGER_STATE_CHANGED = 12   # The gas sensor triggering boolean changed 
    GAS_VALUE_CHANGED = 12           # The gas sensor value changed 

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

    def __init__(self, name, devices = [], level = Level.UNDEFINED,
            neighbors = [], actions = {}, external = False,
            displayIcon = None, displayOrder = 9999):
        """
        Creates a new zone.

        :param str name: the zone name
        :param list(Device) devices: the list of Device objects
        :param zone.Level level: the zone's physical level
        :param list(Neighbor) neighbors: the list of optional neighbor zones.
        :param dict(ZoneEvent -> list(Action)) actions: the optional \
            dictionary from :class:`.ZoneEvent` to :class:`.Action`
        :param bool external: indicates if the zone is external
        :param int displayIcon: the icon associated with the zone, useful
            for displaying in sitemap.
        :param int displayOrder: the order with respective to the other zones,
            useful for arranging in sitemap.
        """

        self.name = name
        self.level = level
        self.devices = [d for d in devices]
        self.neighbors = list(neighbors)
        self.actions = dict(actions) # shallow copy
        self.external = external
        self.displayIcon = displayIcon
        self.displayOrder = displayOrder

    @staticmethod
    def createExternalZone(name, level = Level.FIRST_FLOOR):
        """
        Creates an external zone with the given name.
        :rtype: Zone
        """
        params = { 'name': name, 'level': level, 'external': True }
        return Zone(**params)

    @staticmethod
    def createFirstFloorZone(name):
        """
        Creates an internal first floor zone with the given name.
        :rtype: Zone
        """
        params = { 'name': name, 'level': Level.FIRST_FLOOR }
        return Zone(**params)

    @staticmethod
    def createSecondFloorZone(name):
        """
        Creates an internal second floor zone with the given name.
        :rtype: Zone
        """
        params = { 'name': name, 'level': Level.SECOND_FLOOR }
        return Zone(**params)

    def addDevice(self, device):
        '''
        Creates a new zone that is an exact copy of this one, but has the
        additional device.

        :return: A NEW object.
        :rtype: Zone
        :raise ValueError: if device is None or is not a subclass of :class:`.Device`
        '''
        if None == device:
            raise ValueError('device must not be None')

        if not isinstance(device, Device):
            raise ValueError('device must be an instance of Device')

        newDevices = list(self.devices)
        newDevices.append(device)

        params = self._createCtorParamDictionary('devices', newDevices)
        return Zone(**params)

    def removeDevice(self, device):
        '''
        Creates a new zone that is an exact copy of this one less the given
        device

        :return: A NEW object.
        :rtype: Zone 
        :raise ValueError: if device is None or is not a subclass of :class:`.Device`
        '''
        if None == device:
            raise ValueError('device must not be None')

        if not isinstance(device, Device):
            raise ValueError('device must be an instance of Device')

        newDevices = list(self.devices)
        newDevices.remove(device)

        params = self._createCtorParamDictionary('devices', newDevices)
        return Zone(**params)

    def hasDevice(self, device):
        '''
        Determine if the zone contains the specified device.

        :rtype: Boolean
        '''
        return device in self.devices

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
        :rtype: list(Device)
        '''
        if None == cls:
            raise ValueError('cls must not be None')
        return [d for d in self.devices if isinstance(d, cls)]

    def getDeviceByEvent(self, eventInfo):
        '''
        Returns the device that generates the provided event.

        :param EventInfo eventInfo:
        :rtype: Device
        '''

        if None == eventInfo:
            raise ValueError('eventInfo must not be None')

        return next((d for d in self.devices 
                    if d.containsItem(eventInfo.getItem())), None)

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

        params = self._createCtorParamDictionary('neighbors', newNeighbors)
        return Zone(**params)

    def addAction(self, action):
        '''
        Creates a new zone that is an exact copy of this one, but has the
        additional action mapping.

        :param Action action:
        :return: A NEW object.
        :rtype: Zone 
        '''
        if len(action.getRequiredEvents()) == 0:
            raise ValueError('Action must define at least one triggering event')

        newActions = dict(self.actions)

        for zoneEvent in action.getRequiredEvents():
            if newActions.has_key(zoneEvent):
                newActions[zoneEvent].append(action)
            else:
                newActions[zoneEvent] = [action]

        params = self._createCtorParamDictionary('actions', newActions)
        return Zone(**params)

    def getActions(self, zoneEvent):
        '''
        :return: the list of actions for the provided zoneEvent
        :rtype: list(Action)
        '''
        if self.actions.has_key(zoneEvent):
            return self.actions[zoneEvent]
        else:
            return []

    def getId(self):
        ''' :rtype: str '''
        return str(self.getLevel()) + '_' + self.getName()

    def getName(self):
        ''' :rtype: str '''
        return self.name

    def isInternal(self):
        """
        :return: True if the this is an internal zone
        :rtype: bool
        """
        return not self.isExternal()

    def isExternal(self):
        """
        :return: True if the this is an external zone
        :rtype: bool
        """
        return self.external

    def getLevel(self):
        ''' :rtype: zone.Level'''
        return self.level

    def getDisplayIcon(self):
        ''' :rtype: str or None if not available'''
        return self.displayIcon

    def getDisplayOrder(self):
        ''' :rtype: int'''
        return self.displayOrder

    def getNeighbors(self):
        '''
        :return: a copy of the list of neighboring zones.
        :rtype: list(Neighbor)
        '''
        return list(self.neighbors)

    def getNeighborZones(self, zoneManager, neighborTypes = []):
        '''
        :param list(NeighborType) neighborTypes: optional
        :return: a list of neighboring zones for the provided neighbor type (optional).
        :rtype: list(Zone)
        '''
        if None == zoneManager:
            raise ValueError('zoneManager must not be None')

        if None == neighborTypes or len(neighborTypes) == 0:
            zones = [zoneManager.getZoneById(n.getZoneId()) \
                        for n in self.neighbors]
        else:
            zones = [zoneManager.getZoneById(n.getZoneId()) \
                        for n in self.neighbors \
                        if any(n.getType() == t for t in neighborTypes)]

        return zones

    def containsOpenHabItem(self, item, sensorType = None):
        '''
        Returns True if this zone contains the given itemName; returns False 
        otherwise.

        :param Item item:
        :param Device sensorType: an optional sub-class of Device. If specified,\
            will search for itemName for those device types only. Otherwise,\
            search for all devices/sensors.
        :rtype: bool
        '''
        sensors = self.getDevices() if None == sensorType \
            else self.getDevicesByType(sensorType)
        return any(s.containsItem(item) for s in sensors)

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

    def isOccupied(self, ignoredDeviceTypes = [], secondsFromLastEvent = 5 * 60):
        '''
        Returns an array of two items. The first item is True if - at least one switch turned on, or - a motion event was triggered within the provided # of seconds, or
          - a network device was active in the local network within the
            provided # of seconds.
        If the first item is True, the item is a Device that indicates
        occupancy. Otherwise it is None.

        :param list(Device) ignoredDeviceTypes: the devices not to be
            considered for the occupancy check.
        :rtype: list(bool, Device)
        '''
        for device in self.getDevices():
            if not any(isinstance(device, l) for l in ignoredDeviceTypes):
                if device.isOccupied(secondsFromLastEvent):
                    return (True, device)

        return (False, None)

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

    def onTimerExpired(self, events, item):
        '''
        Determines if the timer item is associated with a switch in this
        zone; if yes, turns off the switch and returns True. Otherwise returns
        False.
        '''
        return False

    def onSwitchTurnedOn(self, events, item, immutableZoneManager):
        '''
        If item belongs to this zone, dispatches the event to the associated
        Switch object, execute the associated actions, and returns True.
        Otherwise return False.

        See :meth:`.Switch.onSwitchTurnedOn`

        :param ImmutableZoneManager immutableZoneManager: a function that \
            returns a Zone object given a zone id string
        :rtype: boolean
        '''
        isProcessed = False
        actions = self.getActions(ZoneEvent.SWITCH_TURNED_ON)

        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON, item, self,
                immutableZoneManager, events)

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOn(events, item.getName()):
                for a in actions:
                    a.onAction(eventInfo)

                isProcessed = True
        
        return isProcessed

    def onSwitchTurnedOff(self, events, item, immutableZoneManager):
        '''
        If item belongs to this zone, dispatches the event to the associated
        Switch object, execute the associated actions, and returns True.
        Otherwise return False.

        See :meth:`.Switch.onSwitchTurnedOff`

        :rtype: boolean
        '''
        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_OFF, item, self,
                immutableZoneManager, events)

        isProcessed = False
        actions = self.getActions(ZoneEvent.SWITCH_TURNED_OFF)

        switches = self.getDevicesByType(Switch)
        for switch in switches:
            if switch.onSwitchTurnedOff(events, item.getName()):
                for a in actions:
                    a.onAction(eventInfo)

                isProcessed = True
        
        return isProcessed

    def dispatchEvent(self, zoneEvent, openHabEvents, item,
            immutableZoneManager, enforceItemInZone):
        '''
        :param ZoneEvent zoneEvent:
        :param scope.events openHabEvents:
        :param ImmutableZoneManager immutableZoneManager:
        :param bool enforceItemInZone: if set to true, the actions won't be
            triggered if the zone doesn't contain the item.
        :rtype: boolean
        '''
        if enforceItemInZone and not self.containsOpenHabItem(item):
            return False 

        return self._invokeActions(zoneEvent, openHabEvents, item,
                immutableZoneManager)


    def _invokeActions(self, zoneEventType, eventDispatcher, item,
            immutableZoneManager):
        '''
        Helper method to invoke actions associated with the event.
        :return: True if event is processed. 
        :rtype: boolean
        '''
        eventInfo = EventInfo(zoneEventType, item, self,
                immutableZoneManager, eventDispatcher)

        processed = False
        for a in self.getActions(zoneEventType):
            if a.onAction(eventInfo):
                processed = True

        return processed

    def __str__(self):
            return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"Zone: {}, floor: {}, {}, displayIcon: {}, displayOrder: {}, {} devices".format(
                self.name,
                self.level,
                ('external' if self.isExternal() else 'internal'),
                self.displayIcon,
                self.displayOrder,
                len(self.devices))
        for d in self.devices:
            str += u"\n  {}".format(unicode(d))

        if len(self.actions) > 0:
            str += u"\n"
            for key in self.actions.keys():
                actionList = self.actions[key]
                for action in actionList:
                    str += u"\n  Action: {} -> {}".format(key, unicode(type(action).__name__))

        if len(self.neighbors) > 0:
            str += u"\n"
            for n in self.neighbors:
                str += u"\n  Neighbor: {}, {}".format(
                        n.getZoneId(), unicode(n.getType()))

        return str

    def _createCtorParamDictionary(self, keyToReplace, newValue):
        """
        A helper method to return a list of ctor parameters.
        
        :param str keyToReplace: the key to override
        :param any newValue: the new value to replace
        :rtype: dict
        """

        params = {
            'name': self.name,
            'devices': self.devices,
            'level': self.level,
            'neighbors': self.neighbors,
            'actions': self.actions,
            'external': self.external,
	    'displayIcon': self.displayIcon,
            'displayOrder': self.displayOrder,
	}
        params[keyToReplace] = newValue

        return params
