from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class Tv(Device):
    '''
    Represents a TV.
    '''

    def __init__(self, powerStatusItem):
        '''
        Ctor

        :param SwitchItem powerStatusItem:
        :raise ValueError: if any parameter is invalid
        '''

        Device.__init__(self, powerStatusItem)

    def isOn(self):
        '''
        Returns true if the TV is on; false otherwise.
        '''
        return PE.isInStateOn(self.getItem().getState())

    def isOff(self):
        '''
        Returns true if the contact is on; false otherwise.
        '''
        return not self.isOn()

    def isOccupied(self, secondsFromLastEvent = 5 * 60):
        '''
        Returns true if the TV is on; returns false otherwise.
        @override

        :rtype: bool
        '''
        return self.isOn()
