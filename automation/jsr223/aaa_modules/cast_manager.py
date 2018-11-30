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

# Pause the passed-in chrome cast player.
# @param casts list of ChromeCast
def pause(casts = CASTS):
    for cast in casts:
        scope.events.sendCommand(cast.getPlayerName(), "PAUSE")

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
# @param url string
# @param casts list of ChromeCast
def playStream(url, casts = CASTS):
    for cast in casts:
        Audio.playStream(cast.getSinkName(), url)

# Return the ChromeCast objects on the first floor.
# @return list of Chromecast
def getFirstFloorCasts():
    return [ CASTS[0] ]

