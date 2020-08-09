from aaa_modules.layout_model.device import Device
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class GasSensor(Device):
    '''
    Represents a generic gas sensor.
    '''

    def __init__(self, valueItem, stateItem):
        '''
        Ctor

        :param org.openhab.core.library.items.NumberItem valueItem: \
            the item to get the value reading
        :param org.openhab.core.library.items.SwitchItem stateItem: \
            the item to get the state reading
        :raise ValueError: if valueItem is invalid
        '''
        Device.__init__(self, valueItem)

        if None == stateItem:
            raise ValueError('stateItem must not be None')

        self.stateItem = stateItem

    def getValue(self):
        '''
        :return: the current sensor value.
        :rtype: int
        '''
        return PE.getIntegerStateValue(self.getItem(), 0)

    def isTriggered(self):
        '''
        :return: true if the gas sensor has detected a high level of
             concentration
        :rtype: bool
        '''
        return PE.isInStateOn(self.stateItem.getState())

class Co2GasSensor(GasSensor):
    ''' Represents a CO2 sensor.  '''
    def __init__(self, valueItem, stateItem):
        GasSensor.__init__(self, valueItem, stateItem)

class NaturalGasSensor(GasSensor):
    ''' Represents a natural gas sensor.  '''
    def __init__(self, valueItem, stateItem):
        GasSensor.__init__(self, valueItem, stateItem)

class SmokeSensor(GasSensor):
    ''' Represents a smoke sensor.  '''
    def __init__(self, valueItem, stateItem):
        GasSensor.__init__(self, valueItem, stateItem)
