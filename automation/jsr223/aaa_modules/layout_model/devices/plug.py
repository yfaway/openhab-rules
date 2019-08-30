from aaa_modules.layout_model.device import Device
from org.eclipse.smarthome.core.library.types import OnOffType

class Plug(Device):
    '''
    Represents a smart plug with optional power reading in Watt.
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
        return OnOffType.ON == self.getItem().getState()

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

        return self.powerReadingItem.getState().intValue()

    def turnOn(self, events):
        '''
        Turns on this plug, if it is not on yet.
        '''
        if OnOffType.ON != self.getItem().getState():
            events.sendCommand(self.getItemName(), "ON")

    def turnOff(self, events):
        '''
        Turn off this plug.
        '''
        if self.isOn():
            events.sendCommand(self.getItemName(), "OFF")
