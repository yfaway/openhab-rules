from aaa_modules.layout_model.device import Device
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class Plug(Device):
    '''
    Represents a smart plug with optional power reading in Watt.
    '''

    POWER_USAGE_THRESHOLD_IN_WATT = 8
    '''
    The plug power usage threshold; if it is above this value, the zone 
    containing this plug is considered to be occupied.
    '''

    def __init__(self, plugItem, powerReadingItem = None):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.SwitchItem plugItem: \
            the item to indicate if the system is in alarm
        :param org.eclipse.smarthome.core.library.items.NumberItem powerReadingItem: \
            the optional item to get the wattage reading
        :raise ValueError: if plugItem is invalid
        '''
        Device.__init__(self, plugItem)

        self.powerReadingItem = powerReadingItem

    def isOn(self):
        '''
        :return: True if the partition is in alarm; False otherwise
        :rtype: bool
        '''
        return PE.isInStateOn(self.getItem().getState())

    def hasPowerReading(self):
        '''
        :return: True if the plug can read the current wattage.
        :rtype: bool
        '''
        return None != self.powerReadingItem

    def getWattage(self):
        '''
        :return: the current wattage of the plug
        :rtype: int or None if the plug has no power reading
        '''
        if None == self.powerReadingItem:
            raise ValueError("Plug has no power reading capability")

        return PE.getIntegerStateValue(self.powerReadingItem, 0)

    def isOccupied(self, secondsFromLastEvent = 5 * 60):
        '''
        Returns True if the power reading is above the threshold.
        @override

        :rtype: bool
        '''

        return self.hasPowerReading() \
            and self.getWattage() > Plug.POWER_USAGE_THRESHOLD_IN_WATT

    def turnOn(self, events):
        '''
        Turns on this plug, if it is not on yet.
        '''
        if not self.isOn():
            events.sendCommand(self.getItemName(), "ON")

    def turnOff(self, events):
        '''
        Turn off this plug.
        '''
        if self.isOn():
            events.sendCommand(self.getItemName(), "OFF")
