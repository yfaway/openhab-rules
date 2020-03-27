# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time
from itertools import ifilter

from org.slf4j import Logger, LoggerFactory
from core import osgi
from core.rules import rule
from core.triggers import when
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from aaa_modules import cast_manager
from aaa_modules.chromecast import *

from aaa_modules.layout_model.devices.activity_times import ActivityTimes

CLASSICAL_MUSIC_URI = "https://wwfm.streamguys1.com/live-mp3"

_SOURCE_ITEM_NAME = 'VT_SelectedChromeCast'
_STREAM_ITEM_NAME = 'VT_SelectedStream'
_MASTER_PLAYER_ITEM_NAME = 'VT_Master_ChromeCastPlayer'

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Update master player control when a chromecast's control state changes.")
@when("Member of gCastPlayer changed")
def updateMasterPlayerState(event):
    if matchSelectedSource(event.itemName):
        events.sendCommand(_MASTER_PLAYER_ITEM_NAME,
                items[event.itemName].toString())

@rule("Update individual cast's player state when master state changes")
@when("Item {0} changed".format(_MASTER_PLAYER_ITEM_NAME))
def updateCastPlayerState(event):
    for cast in cast_manager.CASTS:
        if matchSelectedSource(cast.getPlayerName()):
            if event.itemState == PlayPauseType.PAUSE:
                cast_manager.pause([cast])
            elif event.itemState == PlayPauseType.PLAY:
                cast_manager.resume([cast])

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

@rule("Update the stream selection when the chromecast (source) changes")
@when("Item {0} changed".format(_SOURCE_ITEM_NAME))
def updateStream(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM_NAME])

    if items[_STREAM_ITEM_NAME] == StringType(selectedCasts[0].getStreamName()):
        # same stream as the other cast -> force play
        playMusic(event)
    else: # update the stream item value which will trigger play
        events.sendCommand(_STREAM_ITEM_NAME, selectedCasts[0].getStreamName())

    volumeItemName = selectedCasts[0].getVolumeName()
    volumeState = items[volumeItemName]
    if UnDefType.UNDEF != volumeState and UnDefType.NULL != volumeState:
        events.sendCommand('VT_Master_ChromeCastVolume', 
                str(volumeState.intValue()))

@rule("Play the music when the switch is turn on")
@when("Item VT_Master_PlayMusic changed to ON")
@when("Item VT_SelectedStream changed")
def playMusic(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM_NAME])

    streamName = None
    streamItemValue = items[_STREAM_ITEM_NAME]
    if UnDefType.UNDEF ==  streamItemValue \
        or UnDefType.NULL == streamItemValue \
        or StringType('') == streamItemValue:
        streamName = None
    else:
        streamName = streamItemValue.toString()
    
    if None != streamName:
        cast_manager.playStream(streamName, selectedCasts)
        events.sendCommand(_MASTER_PLAYER_ITEM_NAME, 'PLAY')
    else:
        events.sendCommand(_MASTER_PLAYER_ITEM_NAME, 'PAUSE')

@rule("Pause the music")
@when("Item VT_Master_PlayMusic changed to OFF")
def pauseMusic(event):
    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM_NAME])
    cast_manager.pause(selectedCasts)
    log.info("[Cast] Paused selected stream.")

# Returns True if the item name matches the selected chrome cast (source);
# False otherwise
# @param itemName string
def matchSelectedSource(itemName):
    if UnDefType.UNDEF == items[_SOURCE_ITEM_NAME] \
            or UnDefType.NULL == items[_SOURCE_ITEM_NAME]:
        return False

    selectedCasts = cast_manager.findCasts(items[_SOURCE_ITEM_NAME])
    matchedCast = next(ifilter(lambda item: item.getPrefix() in itemName, 
                selectedCasts), None)
    return None != matchedCast
