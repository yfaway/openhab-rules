from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from org.eclipse.smarthome.model.script.actions.Audio import playSound
from org.eclipse.smarthome.model.script.actions.Audio import playStream
from org.eclipse.smarthome.model.script.actions.Voice import say

import constants
reload(constants)
from constants import *

CLASSICAL_MUSIC_URI = "https://wwfm.streamguys1.com/live-mp3"

# The follow two constants define the morning time range and the # of times
# music will automatically be played. The counter is incremented by one
# when music is played successfully (nothing else was played), and is reset
# each day at 5AM.
MORNING_TIME_RANGE = (6, 9)
MAX_MORNING_MUSIC_START_COUNT = 2

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
morningMusicStartCount = 0

@rule("Play the music when the switch is turn on")
@when("Item VT_GreatRoom_ChromeCastSetUri changed to ON")
# @return True if the new stream is played; False if something else is already
#     playing
def playMusic(event):
    if items['FF_GreatRoom_ChromeCastIdling'] == OnOffType.ON \
            or items['FF_GreatRoom_ChromeCastPlayer'] == PlayPauseType.PAUSE:
        playStream(CLASSICAL_MUSIC_URI)
        return True
    else:
        return False

@rule("Pause the music")
@when("Item VT_GreatRoom_ChromeCastSetUri changed to OFF")
@when("Item {0} changed to {1:d}".format(SECURITY_ITEM_ARM_MODE, SECURITY_STATE_ARM_AWAY))
def pauseMusic(event):
    events.sendCommand('FF_GreatRoom_ChromeCastPlayer', "PAUSE")

@rule("Play music on the first 2 morning visits to kitchen")
@when("Item FF_Kitchen_LightSwitch_MotionSensor changed to ON")
def playMusicInTheMorning(event):
    global morningMusicStartCount

    if isInMorningTimeRange() and \
            morningMusicStartCount < MAX_MORNING_MUSIC_START_COUNT:
        if playMusic(event):
            morningMusicStartCount += 1


@rule("Reset morningMusicStartCount to 0 at 5AM")
@when("Time cron 0 0 5 1/1 * ? *")
def resetMorningMusicStartCount(event):
    morningMusicStartCount = 0

@rule("Stop morning music when front door is open")
@when("Item FF_FrontDoor_Tripped changed to ON")
@when("Item FF_GarageDoor_Tripped changed to ON")
def pauseMorningMusic(event):
    if isInMorningTimeRange():
        pauseMusic(event)

# @return True if the current hour is within the time range; False otherwise.
def isInMorningTimeRange():
    hour = DateTime.now().getHourOfDay()
    return hour >= MORNING_TIME_RANGE[0] and hour < MORNING_TIME_RANGE[1]
