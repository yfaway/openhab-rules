# Contains the rules to manage the chromecast music player (from sitemap),
# as well as rules to automatically play music and announcements in the morning.

import time

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

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Update master player control when a chromecast's control state changes.")
@when("Member of gCastPlayer changed")
def updateMasterPlayerState(event):
    log.info("s0: " + items[event.itemName].toString())
    events.sendCommand('VT_Master_ChromeCastPlayer', items[event.itemName].toString())

@rule("Update individual cast's player state when master state changes")
@when("Item VT_Master_ChromeCastPlayer changed")
def updateCastPlayerState(event):
    for player in ir.getItem('gCastPlayer').members:
        events.sendCommand(player.name, items[event.itemName].toString())

@rule("Update master volume when a chromecast's volume changes.")
@when("Member of gCastVolume changed")
def updateMasterVolume(event):
    events.sendCommand('VT_Master_ChromeCastVolume', str(items[event.itemName].intValue()))

@rule("Update individual cast's volume when master volume changes")
@when("Item VT_Master_ChromeCastVolume changed")
def updateCastVolume(event):
    for volumeItem in ir.getItem('gCastVolume').members:
        events.sendCommand(volumeItem.name, str(items[event.itemName].intValue()))

@rule("Play the music when the switch is turn on")
@when("Item VT_Master_PlayMusic changed to ON")
def playMusic(event):
    cast_manager.playStream(CLASSICAL_MUSIC_URI)

@rule("Pause the music")
@when("Item VT_Master_PlayMusic changed to OFF")
@when("Item {0} changed to {1:d}".format(SECURITY_ITEM_ARM_MODE, SECURITY_STATE_ARM_AWAY))
def pauseMusic(event):
    cast_manager.pause()

#events.postUpdate('VT_Master_ChromeCastVolume', "20")
