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
         ChromeCast('SF_MasterBedroom_ChromeCast', "chromecast:audio:masterBedroom"),
         ChromeCast('SF_MasterWashroom_ChromeCast', "chromecast:audio:masterBathroom")
        ]

_STREAMS = {
    "WWFM Classical": "https://wwfm.streamguys1.com/live-mp3",
    "Venice Classical": "http://174.36.206.197:8000/stream",
    "Portland All Classical": "http://player.allclassical.org/streamplaylist/ac96k.pls",
    "Audiophile Classical": "http://8.38.78.173:8093/stream",
    "113FM Smooth Jazz": "http://113fm-edge2.cdnstream.com:80/1725_128",
    "CD101.9 NY Smooth Jazz": "http://hestia2.cdnstream.com:80/1277_192",
    "Jazz Cafe": "http://radio.wanderingsheep.tv:8000/jazzcafe",
    "Meditation - Yimago Radio 4": "http://199.195.194.94:8109/stream",
    "Santa Radio": "http://149.255.59.164:8041/stream",
    "XMas Music": "http://91.121.134.23:8380/stream",
    "CBC Radio 2": "http://cbcr2tor.akacast.akamaistream.net/7/364/451661/v1/rc.akacast.akamaistream.net/cbc_r2_tor",
    "Classic Rock Florida": "http://198.58.98.83:8258/stream",
    "Radio Paradise - Rock": "http://stream-dc2.radioparadise.com:80/mp3-192",
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
        if scope.OnOffType.ON == scope.items[cast.getIdleItemName()]:
            Audio.playStream(cast.getSinkName(), cast.getStreamUrl())
        else:
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
        else:
            log.info("Missing stream URL for '{0}'".format(name))

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
