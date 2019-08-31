import time

from org.slf4j import Logger, LoggerFactory
from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
from aaa_modules import time_utilities

'''
Play the mindfullness bell every 15 minutes if someone is home and if it is
not sleep time.
'''

# Sound files are in /etc/openhab2/sound folder
BELL_URL = 'bright-tibetan-bell.wav'

@rule("Play mindfullness bell")
@when("Time cron 0 0/15 * 1/1 * ? *")
def playMindfullnessBell(event):
    timeStruct = time.localtime()
    hour = timeStruct[3]

    if hour > 7 and hour <= 23:
        casts = cast_manager.getFirstFloorCasts()

        cast_manager.playSoundFile(BELL_URL, casts, 40)

#playMindfullnessBell(None)
