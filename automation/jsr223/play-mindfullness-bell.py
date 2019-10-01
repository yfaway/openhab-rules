import time

from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
from aaa_modules.security_manager  import SecurityManager as SM

'''
Play the mindfullness bell every 15 minutes if someone is home and if it is
not sleep time.
'''

# Sound files are in /etc/openhab2/sound folder
BELL_URL = 'bell-outside.wav'
BELL_DURATION_IN_SECS = 15

@rule("Play mindfullness bell")
@when("Time cron 0 0/25 * 1/1 * ? *")
def playMindfullnessBell(event):
    timeStruct = time.localtime()
    hour = timeStruct[3]

    if hour <= 7: # not triggered in the night
        return

    # not triggered if house is armed away
    if SM.isArmedAway():
        return

    casts = cast_manager.getFirstFloorCasts()

    volume = 40 if hour >= 20 else 60
    cast_manager.playSoundFile(
            BELL_URL, BELL_DURATION_IN_SECS, casts, volume)

#playMindfullnessBell(None)
