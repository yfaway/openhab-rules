# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time

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

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

CLASSICAL_MUSIC_URI = "https://wwfm.streamguys1.com/live-mp3"

# The follow two constants define the morning time range and the # of times
# announcement and music will automatically be played. The counter is
# incremented by one when music is played successfully (nothing else was
# played), and is reset each day at 5AM.
MORNING_TIME_RANGE = (6, 9)
MAX_MORNING_MUSIC_START_COUNT = 2

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
morningMusicStartCount = 0

@rule("Play the music when the switch is turn on")
@when("Item VT_GreatRoom_ChromeCastSetUri changed to ON")
def playMusic(event):
    if not cast_manager.isActive():
        playStream(CLASSICAL_MUSIC_URI)

@rule("Pause the music")
@when("Item VT_GreatRoom_ChromeCastSetUri changed to OFF")
@when("Item {0} changed to {1:d}".format(SECURITY_ITEM_ARM_MODE, SECURITY_STATE_ARM_AWAY))
def pauseMusic(event):
    cast_manager.pause()

@rule("Play music on the first 2 morning visits to kitchen")
@when("Item FF_Kitchen_LightSwitch_MotionSensor changed to ON")
def playAnnouncementAndMusicInTheMorning(event):
    global morningMusicStartCount

    if isInMorningTimeRange() and \
            morningMusicStartCount < MAX_MORNING_MUSIC_START_COUNT:
        if not cast_manager.isActive():
            msg = getMorningAnnouncement()
            cast_manager.playMessage(msg)

            log.info("playing music")
            time.sleep(1)
            playMusic(event)
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

@rule("Play morning announcement")
@when("Item VT_GreatRoom_PlayMorningAnnouncement changed to ON")
def playMorningAnnouncement(event):
    msg = getMorningAnnouncement()
    log.info("Saying: " + msg)
    say(msg)
    events.sendCommand(event.itemName, 'OFF')

# @return True if the current hour is within the time range; False otherwise.
def isInMorningTimeRange():
    hour = DateTime.now().getHourOfDay()
    return hour >= MORNING_TIME_RANGE[0] and hour < MORNING_TIME_RANGE[1]

# @return a string containing the current's weather and today's forecast.
def getMorningAnnouncement():
    message = 'Good morning. It is {} degree currently; the weather ' \
        'condition is {}. Forecasted temperature range is between {} and {} ' \
        'degrees.'.format(
            items['VT_Weather_Temperature'].intValue(),
            items['VT_Weather_Condition'].toString(),
            items['VT_Weather_ForecastTempMin'].intValue(),
            items['VT_Weather_ForecastTempMax'].intValue())
    if items['VT_Weather_ForecastRain'] > DecimalType(0):
        message += " It is going to rain today."
    elif items['VT_Weather_ForecastSnow'] > DecimalType(0):
        message += " It is going to snow today."

    return message

#cast_manager.pause()
#morningMusicStartCount = 0
#playAnnouncementAndMusicInTheMorning(None)
