'''
Contains functions that work with Google Chromecasts and Google Home.
@see ChromeCast
'''

import time

from org.slf4j import Logger, LoggerFactory
from core import osgi
from core.jsr223 import scope
from core.rules import rule
from core.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from org.eclipse.smarthome.model.script.actions import Audio
from org.eclipse.smarthome.model.script.actions import Voice

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

MAX_SAY_WAIT_TIME_IN_SECONDS = 20

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

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

# If set, the TTS message won't be sent to the chromecasts.
_testMode = False

def pause(casts = CASTS):
    '''
    Pauses the passed-in chrome cast player.

    :param list(ChromeCast) casts:
    '''
    for cast in casts:
        scope.events.sendCommand(cast.getPlayerName(), "PAUSE")

def resume(casts = CASTS):
    '''
    Resumes playing on the passed-in chrome casts.

    :param list(ChromeCast) casts:
    '''
    for cast in casts:
        if scope.OnOffType.ON == scope.items[cast.getIdleItemName()]:
            Audio.playStream(cast.getSinkName(), cast.getStreamUrl())
        else:
            scope.events.sendCommand(cast.getPlayerName(), "PLAY")

def playMessage(message, casts = CASTS, volume = 50):
    '''
    Play the given message on one or more ChromeCast and wait till it finishes 
    (up to MAX_SAY_WAIT_TIME_IN_SECONDS seconds). Afterward, pause the player.
    After this call, cast.isActive() will return False.

    If _testMode is True, no message will be sent to the cast.

    :param str message: the message to tts
    :param list(ChromeCast) casts: 
    :param int volume: the volume value, 0 to 100 inclusive
    :return: boolean True if success; False if stream name is invalid.
    :raise: ValueError if volume is not in the 0 - 100 inclusive range, or if\
    message is None or empty.
    '''
    if volume < 0 or volume > 100:
        raise ValueError('volume must be between 0 and 100')

    if None == message or '' == message:
        raise ValueError('message must not be null or empty')

    for cast in casts:
        scope.events.sendCommand(cast.getVolumeName(), str(volume))
        if not _testMode:
            Voice.say(message, None, cast.getSinkName())

        cast._setLastTtsMessage(message)

    if not _testMode:
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
            else: # announcement is finished.
                seconds = MAX_SAY_WAIT_TIME_IN_SECONDS + 1

        pause(casts)

    return True

def playStream(name, casts = CASTS, volume = None):
    '''
    Play the given stream url.

    :param str name: see _STREAMS
    :param list(ChromeCast) casts:
    :return: boolean True if success; False if stream name is invalid.
    '''

    if None != volume and (volume < 0 or volume > 100):
        raise ValueError('volume must be between 0 and 100')

    url = getStreamUrl(name)
    if None != url:
        for cast in casts:
            if None != volume:
                scope.events.sendCommand(cast.getVolumeName(), str(volume))

            if url == cast.getStreamUrl():
                resume([cast])
            else:
                Audio.playStream(cast.getSinkName(), url)
                cast.setStream(name, url)

        return True
    else:
        logger.info("Missing stream URL for '{0}'".format(name))
        return False

def getAllCasts():
    '''
    Return all available ChromeCast objects.

    :rtype: list(ChromeCast)
    '''

    return CASTS

def getFirstFloorCasts():
    '''
    Return the ChromeCast objects on the first floor.
    :rtype: list(ChromeCast)
    '''
    return [ CASTS[0] ]

def findCasts(prefix):
    '''
    Return a list of ChromeCast. If prefix is UNDEF, NULL, or "ALL", return
    all casts. Otherwise returns the matching casts.

    :param StringItem_or_str prefix:
    :rtype: list(ChromeCast)
    '''
    if scope.UnDefType.UNDEF == prefix \
            or scope.UnDefType.NULL == prefix \
            or scope.StringType("ALL") == prefix \
            or 'ALL' == prefix:
        return CASTS
    elif isinstance(prefix, scope.StringType):
        return filter(lambda cast: cast.getPrefix() == prefix.toString(), CASTS)
    else: # assume to be string
        return filter(lambda cast: cast.getPrefix() == prefix, CASTS)

def getStreamUrl(name):
    '''
    Returns the stream associated with the given name.

    :rtype: str or None if not found
    '''
    if name in _STREAMS:
        return _STREAMS[name]
    else:
        return None

def getAllStreamNames():
    '''
    Returns a list of stream names.

    :rtype: list(str)
    '''
    return _STREAMS.keys()

def _setTestMode(mode):
    '''
    Switches on/off the test mode.

    :param boolean mode:
    '''
    global _testMode
    _testMode = mode
