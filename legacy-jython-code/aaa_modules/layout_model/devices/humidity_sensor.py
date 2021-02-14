from aaa_modules.layout_model.device import Device
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class HumiditySensor(Device):
    '''
    Represents a humidity sensor.
    '''

    def __init__(self, humidityItem):
        '''
        Ctor

        :param NumberItem humidityItem: the item to get the humidity reading
        :raise ValueError: if humidityItem is invalid
        '''
        Device.__init__(self, humidityItem)

    def getHumidity(self):
        '''
        :return: the current humidity level in percentage
        :rtype: int
        '''
        return PE.getIntegerStateValue(self.getItem(), 0)

    def resetValueStates(self):
        ''' Override. '''
        PE.setDecimalState(self.getItem(), -1)
