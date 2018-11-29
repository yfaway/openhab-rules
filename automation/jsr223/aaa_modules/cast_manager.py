# Functions that work with Google Chromecasts and Google Home.
# @TODO create a ChromeCast class to group together the various attributes
# of a Chromecast/Home device.

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
from org.eclipse.smarthome.model.script.actions.Voice import say

from openhab.jsr223 import scope

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

MAX_SAY_WAIT_TIME_IN_SECONDS = 20

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Pause the passed-in chrome cast player.
# @param cast ChromeCast
def pause(cast = ChromeCast('FF_GreatRoom_ChromeCast')):
    scope.events.sendCommand(cast.getPlayerName(), "PAUSE")

# Play the given message and wait till it finishes (up to 
# MAX_SAY_WAIT_TIME_IN_SECONDS seconds). Afterward, pause the player.
# After this call, cast.isActive() will return False.
# @param message string the message to tts
def playMessage(message, cast = ChromeCast('FF_GreatRoom_ChromeCast')):
    say(message)

    # Wait until the cast is available again or a specific number of seconds 
    # has passed. This is a workaround for the limitation that the OpenHab
    # say method is non-blocking.
    seconds = 2
    time.sleep(seconds)
    while seconds <= MAX_SAY_WAIT_TIME_IN_SECONDS:
        if cast.hasTitle(): # this means the announcement is still happening.
            time.sleep(1)
            seconds += 1
        else: # announcemen is finished.
            seconds = MAX_SAY_WAIT_TIME_IN_SECONDS + 1

    pause(cast) # the Player needs to be manually reset to PAUSE.

# Play the given stream url.
# @param url string
def playStream(url, cast = ChromeCast('FF_GreatRoom_ChromeCast')):
    Audio.playStream(url)
