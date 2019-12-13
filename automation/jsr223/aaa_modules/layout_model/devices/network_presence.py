from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class NetworkPresence(Device):
    '''
    Represents a network device. An ON state indicates that the device is
    connected to the local network and thus imply someone is present in the
    zone.
    '''

    def __init__(self, switchItem):
        '''
        :param org.eclipse.smarthome.core.library.items.SwitchItem switchItem:
        :raise ValueError: if any parameter is invalid
        '''

        Device.__init__(self, switchItem)

    def isPresence(self):
        '''
        Returns True if the device is connected to the local network; False
        otherwise.
        '''
        return PE.isInStateOn(self.getItem().getState())


