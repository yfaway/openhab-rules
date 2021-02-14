from aaa_modules.layout_model.device import Device

class AstroSensor(Device):
    '''
    A virtual sensor to determine the light on time; backed by a StringItem.
    '''

    LIGHT_ON_TIMES = ["EVENING", "NIGHT", "BED"]

    def __init__(self, stringItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.StringItem stringItem:
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, stringItem)

    def isLightOnTime(self):
        '''
        Returns True if it is evening time; returns False otherwise.

        :rtype: bool
        '''
        state = self.getItem().getState()
        return any(s == state.toString() for s in self.LIGHT_ON_TIMES)
