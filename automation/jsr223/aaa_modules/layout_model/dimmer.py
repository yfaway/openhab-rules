from core.jsr223 import scope
from org.eclipse.smarthome.core.library.types import OnOffType
    
from aaa_modules.layout_model.switch import Light
from aaa_modules import time_utilities

class Dimmer(Light):
    '''
    Represents a light dimmer with the dimm level value ranges from 1 to 100.
    '''

    def __init__(self, switchItem, timerItem, dimLevel = 5, timeRanges = None,
            illuminanceLevel = None,
            disableTrigeringFromMotionSensor = False):
        '''
        Constructs a new object.

        :raise ValueError: if any parameter is invalid
        '''
        Light.__init__(self, switchItem, timerItem, illuminanceLevel,
                disableTrigeringFromMotionSensor)

        if dimLevel < 0 or dimLevel > 100:
            raise ValueError('dimLevel must be between 0 and 100 inclusive')

        time_utilities.stringToTimeRangeLists(timeRanges) # validate

        self.dimLevel = dimLevel
        self.timeRanges = timeRanges

    def turnOn(self, events):
        '''
        Turn on this light if it is not on yet.
        If the light is dimmable, and if the current time falls into the
        specified time ranges, it will be dimmed; otherwise it is turned on at
        100%. The associated timer item is also turned on.

        @override
        '''
        if OnOffType.ON != self.getItem().getState():
            if time_utilities.isInTimeRange(self.timeRanges):
                events.sendCommand(self.getItemName(),
                        str(self.dimLevel))
            else:
                events.sendCommand(self.getItemName(), "100")

        self._handleCommonOnAction(events)

    def isOn(self):
        '''
        Returns true if the dimmer is turned on; false otherwise.

        @override
        '''
        return self.getItem().state.intValue() > 0

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}, dimLevel: {}, timeRanges: {}".format(
                super(Dimmer, self).__unicode__(), self.dimLevel, self.timeRanges)
