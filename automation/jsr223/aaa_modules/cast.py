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

# Pause the passed-in chrome cast player.
# @param castItemPrefix string the chrome cast item name
def pause(castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    scope.events.sendCommand(castItemPrefix + 'Player', "PAUSE")

# Return true if the the chromecast is playing something.
# @param castItemPrefix string the chrome cast item name
def isActive(castItemPrefix = 'FF_GreatRoom_ChromeCast'):
    return scope.items[castItemPrefix + "Idling"] == scope.OnOffType.OFF \
        and scope.items[castItemPrefix + "Player"] == scope.PlayPauseType.PLAY
