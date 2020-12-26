from core import osgi
from core.jsr223 import scope
from core.rules import rule
from core.triggers import when
from org.eclipse.smarthome.model.script.actions import Audio
from org.eclipse.smarthome.model.script.actions import Voice

SINK_ITEM_NAME = 'AudioVoiceSinkName'

@rule("Play voice TTS message")
@when("Item TextToSpeechMessage changed")
def onTextToSpeechMessageChanged(event):
    ttl = scope.items[event.itemName].toString()
    if ttl is not None and ttl != '':
        Voice.say(ttl, None, scope.items[SINK_ITEM_NAME].toString())

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')

@rule("Play audio stream URL")
@when("Item AudioStreamUrl changed")
def onTextToSpeechMessageChanged(event):
    stream_url = scope.items[event.itemName].toString()
    if stream_url is not None and stream_url != '':
        Audio.playStream(scope.items[SINK_ITEM_NAME].toString(), stream_url)

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')

@rule("Play local audio file")
@when("Item AudioFileLocation changed")
def onTextToSpeechMessageChanged(event):
    file_location = scope.items[event.itemName].toString()
    if file_location is not None and file_location != '':
        Audio.playSound(scope.items[SINK_ITEM_NAME].toString(), file_location)

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')


#scope.events.sendCommand('AudioVoiceSinkName', "chromecast:audio:greatRoom")
#scope.events.sendCommand('AudioFileLocation', 'bell-outside.wav')
#scope.events.sendCommand('AudioStreamUrl', "https://wwfm.streamguys1.com/live-mp3")
#scope.events.sendCommand('TextToSpeechMessage', 'Anna frowns a lot to day')
