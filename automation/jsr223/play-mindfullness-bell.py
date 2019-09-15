import time

from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.zone_manager import ZoneManager
from aaa_modules.layout_model.alarm_partition import AlarmPartition

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
    securityPartitions = ZoneManager.getDevicesByType(AlarmPartition)
    if len(securityPartitions) > 0:
        if AlarmPartition.STATE_ARM_AWAY == securityPartitions[0].getArmMode():
            return

    casts = cast_manager.getFirstFloorCasts()

    volume = 40 if hour >= 20 else 60
    cast_manager.playSoundFile(
            BELL_URL, BELL_DURATION_IN_SECS, casts, volume)

#playMindfullnessBell(None)
