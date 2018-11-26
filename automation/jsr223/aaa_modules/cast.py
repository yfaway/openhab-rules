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

from openhab.jsr223 import scope

MAX_SAY_WAIT_TIME_IN_SECONDS = 20

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Pause the passed-in chrome cast player.
# @param castItemPrefix string the chrome cast item name
def pause(castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    scope.events.sendCommand(castItemPrefix + 'Player', "PAUSE")

# Return true if the the chromecast is playing something.
# @param castItemPrefix string the chrome cast item name
def isActive(castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    return scope.items[castItemPrefix + "Idling"] == scope.OnOffType.OFF \
        and scope.items[castItemPrefix + "Player"] == scope.PlayPauseType.PLAY

def hasTitle(castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    name = castItemPrefix + "Title"
    return scope.UnDefType.UNDEF == scope.items[name] \
        or scope.UnDefType.NULL == scope.items[name] \
        or scope.StringType('') == scope.items[name]

# Play the given message and wait till it finishes (up to 
# MAX_SAY_WAIT_TIME_IN_SECONDS seconds). Afterward, pause the player.
# After this call, isActive() will return False.
# @param message string the message to tts
def playMessage(message, castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    say(message)

    # Wait until the cast is available again or a specific number of seconds 
    # has passed. This is a workaround for the limitation that the OpenHab
    # say method is non-blocking.
    seconds = 2
    time.sleep(seconds)
    while seconds <= MAX_SAY_WAIT_TIME_IN_SECONDS:
        if not hasTitle():
            time.sleep(1)
            seconds += 1
        else:
            seconds = MAX_SAY_WAIT_TIME_IN_SECONDS + 1

    pause(castItemPrefix) # the Player needs to be manually reset to PAUSE.
