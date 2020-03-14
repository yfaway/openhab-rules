import time

from core.jsr223 import scope
from org.eclipse.smarthome.model.script.actions import Audio
from org.eclipse.smarthome.model.script.actions import Voice

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

MAX_SAY_WAIT_TIME_IN_SECONDS = 20

# Constant to fix a bug in OpenHab. For some reasons, OH might invoke the
# script twice.
COMMAND_INTERVAL_THRESHOLD_IN_SECONDS = 30

class ChromeCastAudioSink(Device):
    '''
    Represents a ChromeCast audio sink.
    '''

    def __init__(self, prefix, sinkName):
        '''
        Ctor

        :param str prefix: the item name prefix, as defined in the .item file. By\
            convention, other channels of this device will have this naming \
            pattern: {prefix}Idling, {prefix}Title, {prefix}Player, and so on.
        :param str sinkName: the sink name for voice and audio play. The sink \
            name can be retrieved by running "openhab-cli console" and then \
            "smarthome:audio sinks".
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, PE.createStringItem(
                    'Chromecast-{}-{}'.format(prefix, sinkName)))

        self.sinkName = sinkName
        self.prefix = prefix
        self.streamUrl = None
        self.lastTtsMessage = None
        self._testMode = False

        self._lastCommandTimestamp = time.time()
        self._lastCommand = None

    def playMessage(self, message, volume = 50):
        '''
        Play the given message on one or more ChromeCast and wait till it finishes 
        (up to MAX_SAY_WAIT_TIME_IN_SECONDS seconds). Afterward, pause the player.
        After this call, cast.isActive() will return False.

        If self._testMode is True, no message will be sent to the cast.

        :param str message: the message to tts
        :param int volume: the volume value, 0 to 100 inclusive
        :return: boolean True if success; False if stream name is invalid.
        :raise: ValueError if volume is not in the 0 - 100 inclusive range, or if\
        message is None or empty.
        '''
        if volume < 0 or volume > 100:
            raise ValueError('volume must be between 0 and 100')

        if None == message or '' == message:
            raise ValueError('message must not be null or empty')

        scope.events.sendCommand(self.getVolumeName(), str(volume))
        if not self._testMode:
            Voice.say(message, None, self.getSinkName())

        self.lastTtsMessage = message

        if not self._testMode:
            # Wait until the cast is available again or a specific number of seconds 
            # has passed. This is a workaround for the limitation that the OpenHab
            # 'say' method is non-blocking.
            seconds = 2
            time.sleep(seconds)

            while seconds <= MAX_SAY_WAIT_TIME_IN_SECONDS:
                if self._hasTitle(): # this means the announcement is still happening.
                    time.sleep(1)
                    seconds += 1
                else: # announcement is finished.
                    seconds = MAX_SAY_WAIT_TIME_IN_SECONDS + 1

            self.pause()

        return True

    def playSoundFile(self, localFile, durationInSecs, volume = None):
        '''
        Plays the provided local sound file. See '/etc/openhab2/sound'.
        Returns immediately if the same command was recently executed (see
        COMMAND_INTERVAL_THRESHOLD_IN_SECONDS).

        :param str localFile: a sound file located in '/etc/openhab2/sound'
        :param int durationInSecs: the duration of the sound file in seconds
        :rtype: boolean
        '''

        if localFile == self._lastCommand:
            if (time.time() - self._lastCommandTimestamp) <= COMMAND_INTERVAL_THRESHOLD_IN_SECONDS:
                return

        self._lastCommandTimestamp = time.time()
        self._lastCommand = localFile

        wasActive = self.isActive()
        previousVolume = scope.items[self.getVolumeName()].intValue()

        if None != volume:
            scope.events.sendCommand(self.getVolumeName(), str(volume))

        Audio.playSound(self.getSinkName(), localFile)

        if wasActive:
            time.sleep(durationInSecs + 1)
            scope.events.sendCommand(self.getVolumeName(), str(previousVolume))
            resume()

        return True

    def playStream(self, url, volume = None):
        '''
        Play the given stream url.

        :param str url: 
        :return: boolean True if success; False if stream name is invalid.
        '''

        if None != volume and (volume < 0 or volume > 100):
            raise ValueError('volume must be between 0 and 100.')

        if None == url:
            raise ValueError('url must be specified.')

        if None != volume:
            scope.events.sendCommand(self.getVolumeName(), str(volume))

        if url == self.getStreamUrl():
            resume()
        else:
            Audio.playStream(self.getSinkName(), url)
            self.streamUrl = url

        return True

    def pause(self):
        '''
        Pauses the chrome cast player.
        '''
        scope.events.sendCommand(self.getPlayerName(), "PAUSE")

    def resume(self):
        '''
        Resumes playing.
        '''
        if PE.isInStateOn(scope.items[self.getIdleItemName()]):
            Audio.playStream(self.getSinkName(), self.getStreamUrl())
        else:
            Audio.playStream(self.getSinkName(), self.getStreamUrl())
            scope.events.sendCommand(self.getPlayerName(), "PLAY")

    def isActive(self):
        '''
        Return true if the the chromecast is playing something.

        :param str castItemPrefix: the chrome cast item name
        '''
        return scope.items[self.prefix + "Idling"] == scope.OnOffType.OFF \
            and scope.items[self.getPlayerName()] == scope.PlayPauseType.PLAY

    def _hasTitle(self):
        '''
        :rtype: bool
        '''
        name = self.prefix + "Title"
        return scope.UnDefType.UNDEF != scope.items[name] \
            and scope.UnDefType.NULL != scope.items[name] \
            and scope.StringType('') != scope.items[name]

    def getStreamUrl(self):
        '''
        Returns the current stream Uri or None if no stream set.

        :rtype: str
        '''
        return self.streamUrl

    def getLastTtsMessage(self):
        '''
        :rtype: str
        '''
        return self.lastTtsMessage


    def getPrefix(self):
        '''
        :rtype: str
        '''
        return self.prefix

    def getPlayerName(self):
        '''
        Returns the name of the player item for this chromecast object.

        :rtype: str
        '''
        return self.prefix + "Player"

    def getVolumeName(self):
        '''
        Returns the name of the volume item for this chromecast object.

        :rtype: str
        '''
        return self.prefix + "Volume"

    def getIdleItemName(self):
        '''
        Returns the name of the player item for this chromecast object.

        :rtype: str
        '''
        return self.prefix + "Idling"

    def getSinkName(self):
        '''
        Return the sink name for Voice.say and Audio.playStream usages.

        :rtype: str
        '''
        return self.sinkName


#s = ChromeCastAudioSink('FF_GreatRoom_ChromeCast', "chromecast:audio:greatRoom")
#s.playMessage('the sink name for voice and audio play. The sink \
#            name can be retrieved by running', 30)
#s.playSoundFile('bell-outside.wav', 15, 30)
#s.playStream("https://wwfm.streamguys1.com/live-mp3", 30)
#s.pause()
