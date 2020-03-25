from aaa_modules.layout_model.device import Device
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class IlluminanceSensor(Device):
    '''
    Represents a light/illuminance sensor; the underlying OpenHab object is a
    NumberItem.
    '''

    def __init__(self, numberItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.NumberItem numberItem:
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, numberItem)

    def getIlluminanceLevel(self):
        '''
        Returns an positive integer representing the LUX value.
        '''
        if PE.isStateAvailable(self.getItem().getState()):
            return self.getItem().getState().intValue()
        else:
            return 0
