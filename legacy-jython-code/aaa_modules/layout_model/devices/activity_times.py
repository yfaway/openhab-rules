from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

from aaa_modules import time_utilities

class ActivityTimes(Device):
    '''
    Represents a virtual device that represent the activities within the zone.
    This device has no real backed OpenHab item.
    '''

    def __init__(self, timeRangeMap):
        '''
        Ctor

        :param dictionary timeRangeMap: a map from activity string to time \
            range string \
            The supported activities are 'lunch', 'dinner', 'sleep', 'quiet', \
            'wakeup'.
            A time range string can be a single or multiple \
            ranges in the 24-hour format.\
            Example: '10-12', or '6-9, 7-7, 8:30 - 14:45', or '19 - 8' \
            (wrap around)
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, PE.createStringItem('ActivityTimesItem'))

        acceptableKeys = ['lunch', 'dinner', 'sleep', 'quiet', 'wakeup']
        for key in timeRangeMap.keys():
            if key not in acceptableKeys:
                raise ValueError('Invalid time range key {}'.format(key))
        
        self.timeRangeMap = timeRangeMap

    def isLunchTime(self, epochSeconds = None):
        return self._isInTimeRange('lunch', epochSeconds)

    def isDinnerTime(self, epochSeconds = None):
        return self._isInTimeRange('dinner', epochSeconds)

    def isQuietTime(self, epochSeconds = None):
        return self._isInTimeRange('quiet', epochSeconds)

    def isSleepTime(self, epochSeconds = None):
        return self._isInTimeRange('sleep', epochSeconds)

    def isWakeupTime(self, epochSeconds = None):
        return self._isInTimeRange('wakeup', epochSeconds)

    def _isInTimeRange(self, key, epochSeconds):
        if key not in self.timeRangeMap.keys():
            return False

        timeRangeString = self.timeRangeMap[key]
        return time_utilities.isInTimeRange(timeRangeString, epochSeconds)
