'''
Utility class containing a set of time related functions.
'''

import time

def isInTimeRange(timeRangesString, epochSeconds = None):
    '''
    Determines if the current time is in the timeRange string.

    :param str timeRangesString: one or multiple time range in 24-hour format.\
        Example: '10-12', or '6-9, 7-7, 8:30 - 14:45', or '19 - 8' (wrap around)
    :param int epochSeconds: seconds since epoch, optional
    :rtype: boolean
    :raise: ValueError if the time range string is invalid
    '''

    if None == timeRangesString or 0 == len(timeRangesString):
        raise ValueError('Must have at least one time range.')

    timeStruct = time.localtime(epochSeconds)
    hour = timeStruct[3]
    minute = timeStruct[4]

    for range in stringToTimeRangeLists(timeRangesString):
        startHour, startMinute, endHour, endMinute = range
        if startHour <= endHour: 
            if hour < startHour:
                continue
        else: # wrap around scenario
            pass

        if hour == startHour and minute < startMinute:
            continue

        if endMinute == 0:
            if startHour <= endHour:
                if hour >= endHour:
                    continue
            else: # wrap around
                if (hour < startHour or hour > 23) and (hour < 0 or hour > endHour):
                    continue
        else: # minutes are > 0
            if hour > endHour or minute > endMinute:
                continue

        return True

    return False

def stringToTimeRangeLists(timeRangesString):
    '''
    Return a list of time ranges. Each list item is itself a list of 4 elements:
    startTime, startMinute, endTime, endMinute.

    :rtype: list
    :raise: ValueError if the time range string is invalid
    '''
    if None == timeRangesString or 0 == len(timeRangesString):
        raise ValueError('Must have at least one time range.')

    timeRanges = []
    pairs = timeRangesString.split(',')
    for pair in pairs:
        times = pair.split('-')
        if 1 == len(times):
            hour = int(times[0])
            if hour < 0 or hour > 23:
                raise ValueError('Hour must be between 0 and 23 inclusive.')
            timeRanges.append([int(hour), 0, int(hour), 59])
        elif 2 == len(times):
            thisRange = []

            def parseHourAndMinute(str):
                hourMinute = str.split(':')
                hour = int(hourMinute[0])
                if hour < 0 or hour > 23:
                    raise ValueError('Hour must be between 0 and 23 inclusive.')

                if 1 == len(hourMinute):
                    return [int(hour), 0] # 0 minute
                elif 2 == len(hourMinute):
                    minute = int(hourMinute[1])
                    if minute < 0 or minute > 59:
                        raise ValueError('Minute must be between 0 and 59 inclusive.')
                    return [hour, minute]
                else:
                    raise ValueError('Must be in format "HH" or "HH:MM".')

            thisRange += parseHourAndMinute(times[0])
            thisRange += parseHourAndMinute(times[1])

            timeRanges.append(thisRange)
        else:
            raise ValueError('Must have either one or two time values.')

    return timeRanges

