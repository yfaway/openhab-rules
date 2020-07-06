import time

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class MotionSensor(Device):
    '''
    Represents a motion sensor; the underlying OpenHab object is a SwitchItem.
    '''

    def __init__(self, switchItem, batteryPowered = True):
        '''
        :param org.eclipse.smarthome.core.library.items.SwitchItem switchItem:
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, switchItem, batteryPowered)

    def isOn(self):
        '''
        Returns true if the motion sensor's state is on; false otherwise.
        '''
        return PE.isInStateOn(self.getItem().getState())

    def isOccupied(self, minutesFromLastMotionEvent = 5):
        '''
        Returns true if a motion event was triggered within the provided # of
        minutes. Returns false otherwise.

        :rtype: bool
        '''
        if self.isOn():
            return True

        if None == self.getLastActivatedTimestamp():
            return False
        else:
            elapsedTime = time.time() - self.getLastActivatedTimestamp()
            return elapsedTime < (minutesFromLastMotionEvent * 60)

    def onMotionSensorTurnedOn(self, events, itemName):
        '''
        Handled the motion sensor ON event.

        :rtype: True if itemName matches this sensor; False otherwise.
        '''
        matched = self.getItemName() == itemName 

        self._updateLastActivatedTimestamp()

        return matched
