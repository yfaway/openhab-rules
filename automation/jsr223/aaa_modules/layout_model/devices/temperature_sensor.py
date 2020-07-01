from aaa_modules.layout_model.device import Device
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class TemperatureSensor(Device):
    '''
    Represents a temperature sensor.
    '''

    def __init__(self, temperatureItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.NumberItem temperatureItem: \
            the item to get the humidity reading
        :raise ValueError: if temperatureItem is invalid
        '''
        Device.__init__(self, temperatureItem)

    def getTemperature(self):
        '''
        :return: the current temperature in degree.
        :rtype: int
        '''
        return PE.getIntegerStateValue(self.getItem(), 0)
