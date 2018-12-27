import time

# @param epochSeconds int seconds since epoch, optional
# @return true if it is kids' nap or sleep time.
def isKidsSleepTime(epochSeconds = None):
    timeStruct = time.localtime(epochSeconds)
    hourOfDay = timeStruct[3]
    if hourOfDay >= 21 or hourOfDay < 8: # regular sleep time
        return True
    elif hourOfDay >= 13 and hourOfDay <= 16: # nap time
        dayOfWeek = timeStruct[6]
        return dayOfWeek == 5 or dayOfWeek == 6 # weekend
    else:
        return False
