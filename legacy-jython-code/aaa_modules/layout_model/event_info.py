
class EventInfo(object):
    """
    Represent an event such as switch turned on, switch turned off, or
    motion triggered.
    """

    def __init__(self, eventType, item, zone, zoneManager, events):
        """
        Creates a new EventInfo object.

        :param ZoneEvent eventType: the type of the event
        :param Item item: the OpenHab Item
        :param Zone zone: the zone where the event was triggered
        :param ImmutableZoneManager zoneManager:
        :param scope.events events: the OpenHab events object to dispatch actions
        """

        if None == eventType:
            raise ValueError('eventType must not be None')

        if None == item:
            raise ValueError('item must not be None')

        if None == zone:
            raise ValueError('zone must not be None')

        if None == events:
            raise ValueError('events must not be None')

        self.eventType = eventType
        self.item = item
        self.zone = zone
        self.zoneManager = zoneManager
        self.events = events

    def getEventType(self):
        ''' :rtype: ZoneEvent'''
        return self.eventType

    def getItem(self):
        ''' :rtype: Item'''
        return self.item

    def getZone(self):
        ''' :rtype: Zone'''
        return self.zone

    def getZoneManager(self):
        ''' :rtype: ImmutableZoneManager'''
        return self.zoneManager

    def getEventDispatcher(self):
        ''' :rtype: Event'''
        return self.events
