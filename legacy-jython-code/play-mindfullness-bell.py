import core
from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.security_manager  import SecurityManager as SM
from aaa_modules.layout_model.devices.activity_times import ActivityTimes

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

    # not triggered if house is armed away
    if SM.isArmedAway(zm):
        return

    volume = 40

    activity = zm.getDevicesByType(ActivityTimes)[0]
    if activity.isSleepTime():
        return
    elif activity.isQuietTime():
        volume = 40
    else:
        volume = 60

    casts = cast_manager.getFirstFloorCasts()
    cast_manager.playSoundFile(
            BELL_URL, BELL_DURATION_IN_SECS, casts, volume)

#playMindfullnessBell(None)
