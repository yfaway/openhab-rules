# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time
from itertools import ifilter

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

import constants
reload(constants)
from constants import *

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

CLASSICAL_MUSIC_URI = "https://wwfm.streamguys1.com/live-mp3"

_SOURCE_ITEM = 'VT_SelectedChromeCast'
_STREAM_ITEM = 'VT_SelectedStream'

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Update master player control when a chromecast's control state changes.")
@when("Member of gCastPlayer changed")
def updateMasterPlayerState(event):
    if matchSelectedSource(event.itemName):
        events.sendCommand('VT_Master_ChromeCastPlayer',
                items[event.itemName].toString())

@rule("Update individual cast's player state when master state changes")
@when("Item VT_Master_ChromeCastPlayer changed")
def updateCastPlayerState(event):
    for player in ir.getItem('gCastPlayer').members:
        if matchSelectedSource(player.name):
            events.sendCommand(player.name, items[event.itemName].toString())

@rule("Update master volume when a chromecast's volume changes.")
@when("Member of gCastVolume changed")
def updateMasterVolume(event):
    if matchSelectedSource(event.itemName):
        events.sendCommand('VT_Master_ChromeCastVolume', 
                str(items[event.itemName].intValue()))

@rule("Update individual cast's volume when master volume changes")
@when("Item VT_Master_ChromeCastVolume changed")
def updateCastVolume(event):
    for volumeItem in ir.getItem('gCastVolume').members:
        if matchSelectedSource(volumeItem.name):
            events.sendCommand(volumeItem.name, str(items[event.itemName].intValue()))

@rule("Update the stream selection and play the music when the switch is turn on")
@when("Item VT_SelectedChromeCast changed")
def updateStream(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])
    events.sendCommand(_STREAM_ITEM, selectedCasts[0].getStreamName())

@rule("Play the music when the switch is turn on")
@when("Item VT_Master_PlayMusic changed to ON")
@when("Item VT_SelectedStream changed")
def playMusic(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])

    streamName = None
    itemValue = items[_STREAM_ITEM]
    if UnDefType.UNDEF ==  itemValue or UnDefType.NULL == itemValue:
        streamName = None
    else:
        streamName = itemValue.toString()
    
    if None != streamName:
        cast_manager.playStream(streamName, selectedCasts)
    else:
        log.info("Invalid stream " + itemValue.toString())

@rule("Pause the music")
@when("Item VT_Master_PlayMusic changed to OFF")
@when("Item {0} changed to {1:d}".format(SECURITY_ITEM_ARM_MODE, SECURITY_STATE_ARM_AWAY))
def pauseMusic(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])
    cast_manager.pause(selectedCasts)

# Returns True if the item name matches the selected chrome cast (source);
# False otherwise
# @param itemName string
def matchSelectedSource(itemName):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])
    matchedCast = next(ifilter(lambda item: item.getPrefix() in itemName, 
                selectedCasts), None)
    return None != matchedCast
