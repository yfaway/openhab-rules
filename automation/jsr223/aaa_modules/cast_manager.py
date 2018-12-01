# Functions that work with Google Chromecasts and Google Home.
# @see ChromeCast

import time

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from org.eclipse.smarthome.model.script.actions import Audio
from org.eclipse.smarthome.model.script.actions import Voice

from openhab.jsr223 import scope

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

MAX_SAY_WAIT_TIME_IN_SECONDS = 20

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

CASTS = [ChromeCast('FF_GreatRoom_ChromeCast', "chromecast:audio:greatRoom"),
         ChromeCast('SF_MasterBedRoom_ChromeCast', "chromecast:audio:masterBedRoom")]

_STREAMS = {
    "Classical": "https://wwfm.streamguys1.com/live-mp3",
    "Venice Classical": "http://174.36.206.197:8000/stream",
    "Portland All Classical": "http://player.allclassical.org/streamplaylist/ac96k.pls",
    "Audiophile Classical": "http://8.38.78.173:8093/stream",
    "Jazz Cafe": "http://radio.wanderingsheep.tv:8000/jazzcafe",
    "CBC Radio 2": "http://cbcr2tor.akacast.akamaistream.net/7/364/451661/v1/rc.akacast.akamaistream.net/cbc_r2_tor"
}

# Pauses the passed-in chrome cast player.
# @param casts list of ChromeCast
def pause(casts = CASTS):
    for cast in casts:
        scope.events.sendCommand(cast.getPlayerName(), "PAUSE")

# Resumes playing on the passed-in chrome casts.
# @param casts list of ChromeCast
def resume(casts = CASTS):
    for cast in casts:
        scope.events.sendCommand(cast.getPlayerName(), "PLAY")

# Play the given message on one or more ChromeCast and wait till it finishes 
# (up to MAX_SAY_WAIT_TIME_IN_SECONDS seconds). Afterward, pause the player.
# After this call, cast.isActive() will return False.
# @param message string the message to tts
# @param casts list of ChromeCast
def playMessage(message, casts = CASTS):
    for cast in casts:
        Voice.say(message, None, cast.getSinkName())

    # Wait until the cast is available again or a specific number of seconds 
    # has passed. This is a workaround for the limitation that the OpenHab
    # say method is non-blocking.
    seconds = 2
    time.sleep(seconds)

    lastCast = casts[-1]
    while seconds <= MAX_SAY_WAIT_TIME_IN_SECONDS:
        if lastCast.hasTitle(): # this means the announcement is still happening.
            time.sleep(1)
            seconds += 1
        else: # announcemen is finished.
            seconds = MAX_SAY_WAIT_TIME_IN_SECONDS + 1

    pause(casts)

# Play the given stream url.
# @param name string; see _STREAMS
# @param casts list of ChromeCast
def playStream(name, casts = CASTS):
    for cast in casts:
        url = getStreamUrl(name)
        if None != url:
            if url == cast.getStreamUrl():
                resume([cast])
            else:
                Audio.playStream(cast.getSinkName(), url)
                cast.setStream(name, url)

# Return the ChromeCast objects on the first floor.
# @return list of Chromecast
def getFirstFloorCasts():
    return [ CASTS[0] ]

# Return a list of ChromeCast 
# @param prefix the state of a StringItem
def findCasts(prefix):
    if scope.UnDefType.UNDEF == prefix \
            or scope.UnDefType.NULL == prefix \
            or scope.StringType("ALL") == prefix:
        return CASTS
    else:
        return filter(lambda cast: cast.getPrefix() == prefix.toString(), CASTS)

# Returns the stream associated with the given name.
# @return string could be None if not found
def getStreamUrl(name):
    if name in _STREAMS:
        return _STREAMS[name]
    else:
        return None