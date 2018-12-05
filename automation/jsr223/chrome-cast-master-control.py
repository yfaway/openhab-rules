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

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

from aaa_modules import security_manager
reload(security_manager)
from aaa_modules import security_manager

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
    # Reset to empty string so that we can trigger a change event, just in 
    # case the current cast's stream is the same as the other cast's.
    events.sendCommand(_STREAM_ITEM, '')
    events.sendCommand(_STREAM_ITEM, selectedCasts[0].getStreamName())

@rule("Play the music when the switch is turn on")
@when("Item VT_Master_PlayMusic changed to ON")
@when("Item VT_SelectedStream changed")
def playMusic(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])

    streamName = None
    streamItemValue = items[_STREAM_ITEM]
    if UnDefType.UNDEF ==  streamItemValue or UnDefType.NULL == streamItemValue:
        streamName = None
    else:
        streamName = streamItemValue.toString()
    
    if None != streamName:
        cast_manager.playStream(streamName, selectedCasts)
    else:
        log.info("Invalid stream " + itemValue.toString())

@rule("Pause the music")
@when("Item VT_Master_PlayMusic changed to OFF")
@when(security_manager.WHEN_CHANGED_TO_ARMED_AWAY)
def pauseMusic(event):
    if security_manager.ITEM_NAME_PARTITION_ARM_MODE == event.itemName:
        cast_manager.pause()
    else:
        selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])
        cast_manager.pause(selectedCasts)

@rule("Play music when a bathroom fan is turned on")
@when("Member of gFanSwitch changed to ON")
def playMusicWhenBathroomFanTurnOn(event):
    index = event.itemName.rfind("_")
    castPrefix = event.itemName[0:index] + "_ChromeCast"
    casts = cast_manager.findCasts(StringType(castPrefix))
    cast_manager.playStream("CD101.9 NY Smooth Jazz", casts)

@rule("Stop music when a bathroom fan is turned off")
@when("Member of gFanSwitch changed to OFF")
@when("Member of gSecondFloorLightSwitch changed to OFF")
def playMusicWhenBathroomFanTurnOff(event):
    index = event.itemName.rfind("_")
    castPrefix = event.itemName[0:index] + "_ChromeCast"
    casts = cast_manager.findCasts(StringType(castPrefix))
    cast_manager.pause(casts)

# Returns True if the item name matches the selected chrome cast (source);
# False otherwise
# @param itemName string
def matchSelectedSource(itemName):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM])
    matchedCast = next(ifilter(lambda item: item.getPrefix() in itemName, 
                selectedCasts), None)
    return None != matchedCast
