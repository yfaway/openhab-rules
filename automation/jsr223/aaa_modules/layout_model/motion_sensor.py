import time
from org.eclipse.smarthome.core.library.types import OnOffType

from aaa_modules.layout_model import device
reload(device)
from aaa_modules.layout_model.device import Device

# Represents a motion sensor; the underlying OpenHab object is a SwitchItem.
class MotionSensor(Device):
    # Ctor
    # @param switchItem org.eclipse.smarthome.core.library.items.SwitchItem
    # @throw ValueError if any parameter is invalid
    def __init__(self, switchItem):
        Device.__init__(self, switchItem)
        self.lastOnTimestamp = -1

    # Returns true if the motion sensor's state is on; false otherwise.
    def isOn(self):
        return OnOffType.ON == self.getItem().getState()

    # Returns true if a motion event was triggered within the provided # of
    # minutes. Returns false otherwise.
    # @return bool
    def isOccupied(self, minutesFromLastMotionEvent = 5):
        if self.isOn():
            return True

        elapsedTime = time.time() - self.lastOnTimestamp
        return elapsedTime < (minutesFromLastMotionEvent * 60)

    # Handled the motion sensor ON event.
    # @return True if itemName matches this sensor; False otherwise.
    def onMotionSensorTurnedOn(self, events, itemName):
        matched = self.getItemName() == itemName 

        self.lastOnTimestamp = time.time()

        return matched

    # @override
    def __unicode__(self):
        return u"{}, lastOnTimestamp: {}".format(
                super(MotionSensor, self).__unicode__(), self.lastOnTimestamp)
