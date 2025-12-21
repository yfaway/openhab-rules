from java.time import ZonedDateTime

from core import osgi

from core.jsr223.scope import actions
from core.jsr223 import scope
from core.rules import rule
from core.triggers import when
from org.slf4j import Logger, LoggerFactory
from org.openhab.core.model.script.actions import Audio
from org.openhab.core.model.script.actions import Voice

ECOBEE_ID = '411921197263'
SINK_ITEM_NAME = 'AudioVoiceSinkName'

logger = LoggerFactory.getLogger("org.openhab.core.model.script.Rules")

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
def onAudioStreamUrlChanged(event):
    stream_url = scope.items[event.itemName].toString()
    if stream_url is not None and stream_url != '':
        Audio.playStream(scope.items[SINK_ITEM_NAME].toString(), stream_url)

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')

@rule("Play local audio file")
@when("Item AudioFileLocation changed")
def onAudioFileLocationChanged(event):
    file_location = scope.items[event.itemName].toString()
    if file_location is not None and file_location != '':
        Audio.playSound(scope.items[SINK_ITEM_NAME].toString(), file_location)

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')

@rule("Send email")
@when("Item EmailAddresses changed")
def onEmailAddressesChanged(event):
    email_addresses = scope.items[event.itemName].toString()
    if email_addresses is not None and email_addresses != '':
        attachmentState = scope.items['EmailAttachmentUrls']
        if scope.UnDefType.NULL ==  attachmentState \
                or scope.UnDefType.UNDEF == attachmentState \
                or attachmentState.toString() == '':
            attachment_urls = []
        else: 
            attachment_urls = attachmentState.toString().split(', ')

        bodyState = scope.items['EmailBody']
        if scope.UnDefType.NULL ==  bodyState or scope.UnDefType.UNDEF == bodyState:
            body = ''
        else:
            body = bodyState.toString()

        logger.info(u"Sending email to '{}' for subject '{}', body '{}'".format(
                email_addresses,
                scope.items['EmailSubject'].toString(),
                scope.items['EmailBody']))

        actions.get("mail", "mail:smtp:gmail").sendMail(
                email_addresses,
                scope.items['EmailSubject'].toString(),
                body)

        # reset the item to wait for the next message.
        scope.events.sendCommand(event.itemName, '')
        scope.events.sendCommand("EmailSubject", '')
        scope.events.sendCommand("EmailBody", '')
        scope.events.sendCommand("EmailAttachmentUrls", '')

@rule("Change Ecobee thermostat mode.")
@when("Item EcobeeThermostatHoldMode changed")
def on_ecobee_thermostat_hold_mode_changed(event):
    hold_mode = scope.items[event.itemName].toString()
    action = actions.get("ecobee", "ecobee:thermostat:account:411921197263")
    if hold_mode is not None and hold_mode != '':
        action.setHold(hold_mode)

        scope.events.sendCommand(event.itemName, '')
        logger.info(u"Changed Ecobee thermostat to '{}'.".format(hold_mode))

@rule("Resume Ecobee thermostat.")
@when("Item EcobeeThermostatResume changed to ON")
def on_ecobee_thermostat_hold_mode_changed(event):
    scope.events.sendCommand(event.itemName, 'OFF')

    action = actions.get("ecobee", "ecobee:thermostat:account:411921197263")
    action.resumeProgram(True)
    logger.info(u"Resumed Ecobee thermostat.")


#scope.events.sendCommand('EmailSubject', 'Test subject')
#scope.events.sendCommand('EmailBody', 'Test body')
#scope.events.sendCommand('EmailAttachmentUrls', '')
#scope.events.sendCommand('EmailAddresses', 'haipham@gmail.com')

#scope.events.sendCommand('AudioVoiceSinkName', "chromecast:audio:greatRoom")
#scope.events.sendCommand('AudioFileLocation', 'bell-outside.wav')
#scope.events.sendCommand('AudioStreamUrl', "https://wwfm.streamguys1.com/live-mp3")
#scope.events.sendCommand('TextToSpeechMessage', 'Anna frowns a lot to day')

#scope.events.sendCommand('EcobeeThermostatHoldMode', "away")
#scope.events.sendCommand('EcobeeThermostatResume', "ON")
