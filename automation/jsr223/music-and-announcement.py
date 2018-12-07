# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.joda.time import DateTime

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

# The follow two constants define the morning time range and the # of times
# announcement and music will automatically be played. The counter is
# incremented by one when music is played successfully (nothing else was
# played), and is reset each day at 5AM.
MORNING_TIME_RANGE = (6, 9)
MAX_MORNING_MUSIC_START_COUNT = 2

# If set, implies the user hasn't left yet, and thus do not trigger additional
# annoucement.
inSession = False

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
morningMusicStartCount = 0

@rule("Play music on the first 2 morning visits to kitchen")
@when("Item FF_Kitchen_LightSwitch_MotionSensor changed to ON")
def playAnnouncementAndMusicInTheMorning(event):
    global morningMusicStartCount
    global inSession

    if isInMorningTimeRange() and \
            morningMusicStartCount < MAX_MORNING_MUSIC_START_COUNT:
        if not inSession:
            inSession = True
            msg = getMorningAnnouncement()
            casts = cast_manager.getFirstFloorCasts()

            cast_manager.playMessage(msg, casts)
            cast_manager.playStream("WWFM Classical", casts)
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
        inSession = False

@rule("Play morning announcement")
@when("Item VT_GreatRoom_PlayMorningAnnouncement changed to ON")
def playMorningAnnouncement(event):
    msg = getMorningAnnouncement()
    log.info("Saying: " + msg)
    cast_manager.playMessage(msg)
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
