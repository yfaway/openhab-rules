# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time

from org.slf4j import Logger, LoggerFactory
from core import osgi
from core.rules import rule
from core.triggers import when
from org.joda.time import DateTime

from aaa_modules import cast_manager
from aaa_modules import time_utilities
from aaa_modules.environment_canada import Forecast, EnvCanada

# The follow two constants define the morning time range and the # of times
# announcement and music will automatically be played. The counter is
# incremented by one when music is played successfully (nothing else was
# played), and is reset each day at 5AM.
MORNING_TIME_RANGE = (6, 9)
MAX_MORNING_MUSIC_START_COUNT = 2

LOG_PREFIX = '[Morning Annoucement]'

# If set, implies the user hasn't left yet, and thus do not trigger additional
# annoucement.
inMorningSession = False

# Indicates if music was already played at dinner time.
inDinnerSession = False

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")
morningMusicStartCount = 0

@rule("Play music on the first 2 morning visits to kitchen")
@when("Item FF_Kitchen_LightSwitch_MotionSensor changed to ON")
def playAnnouncementAndMusicInTheMorning(event):
    global morningMusicStartCount
    global inMorningSession

    if isInMorningTimeRange() and \
            morningMusicStartCount < MAX_MORNING_MUSIC_START_COUNT:
        if not inMorningSession:
            logger.info('{} Playing morning annoucement.'.format(LOG_PREFIX))
            inMorningSession = True
            msg = getMorningAnnouncement()
            casts = cast_manager.getFirstFloorCasts()

            cast_manager.playMessage(msg, casts)
            cast_manager.playStream("WWFM Classical", casts)
            morningMusicStartCount += 1
#        else:
#            logger.info('{} Not in session.'.format(LOG_PREFIX))

@rule("Reset music states at 5AM")
@when("Time cron 0 0 5 1/1 * ? *")
def resetMusicStates(event):
    global morningMusicStartCount
    global inMorningSession
    global inDinnerSession

    morningMusicStartCount = 0
    inMorningSession = False
    inDinnerSession = False

@rule("Stop morning music when front door is open")
@when("Item FF_FrontDoor_Tripped changed to ON")
@when("Item FF_GarageDoor_Tripped changed to ON")
def pauseMorningMusic(event):
    global inMorningSession
    if isInMorningTimeRange() and inMorningSession:
        logger.info('{} Pausing morning music.'.format(LOG_PREFIX))
        cast_manager.pause()
        inMorningSession = False

@rule("Play morning announcement when click on a button")
@when("Item VT_GreatRoom_PlayMorningAnnouncement changed to ON")
def playMorningAnnouncement(event):
    msg = getMorningAnnouncement()
    logger.info(u"{} Saying: {}".format(LOG_PREFIX, msg))
    cast_manager.playMessage(msg)
    events.sendCommand(event.itemName, 'OFF')

@rule("Play music at dinner time")
@when("Item FF_Kitchen_LightSwitch_MotionSensor changed to ON")
def playMusicAtDinnerTime(event):
    global inDinnerSession
    if time_utilities.isDinnerTime():
        if not inDinnerSession:
            casts = cast_manager.getFirstFloorCasts()
            cast_manager.playStream("Meditation - Yimago Radio 4", casts, 40)

            inDinnerSession = True

# @return True if the current hour is within the time range; False otherwise.
def isInMorningTimeRange():
    hour = DateTime.now().getHourOfDay()
    return hour >= MORNING_TIME_RANGE[0] and hour < MORNING_TIME_RANGE[1]

# @return a string containing the current's weather and today's forecast.
def getMorningAnnouncement():
    message = u'Good morning. It is {} degree currently; the weather ' \
        'condition is {}. Forecasted temperature range is between {} and {} ' \
        'degrees.'.format(
            items['VT_Weather_Temperature'].intValue(),
            items['VT_Weather_Condition'].toString(),
            items['VT_Weather_ForecastTempMin'].intValue(),
            items['VT_Weather_ForecastTempMax'].intValue())

    forecasts = EnvCanada.retrieveHourlyForecast('Ottawa', 12)
    rainPeriods = [f for f in forecasts if \
                 'High' == f.getPrecipationProbability() or \
                 'Medium' == f.getPrecipationProbability()]
    if len(rainPeriods) > 0:
        if len(rainPeriods) == 1:
            message += u" There will be precipation at {}.".format(
                    rainPeriods[0].getUserFriendlyForecastTime())
        else:
            message += u" There will be precipation from {} to {}.".format(
                    rainPeriods[0].getUserFriendlyForecastTime(),
                    rainPeriods[-1].getUserFriendlyForecastTime())

    return message

#morningMusicStartCount = 0
#inDinnerSession = False
#playMusicAtDinnerTime(None)
