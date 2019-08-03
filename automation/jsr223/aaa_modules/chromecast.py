'''
Represents a Chromecast, Chromecast Audio, or a Google Home device.
'''

from org.slf4j import Logger, LoggerFactory
from core.jsr223 import scope

LOG = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class ChromeCast:
    '''
    Ctor.

    :param str prefix: the item name prefix, as defined in the .item file. By\
        convention, other channels of this device will have this naming \
        pattern: {prefix}Idling, {prefix}Title, {prefix}Player, and so on.
    :param str sinkName: the sink name for voice and audio play. The sink \
        name can be retrieved by running "openhab-cli console" and then \
        "smarthome:audio sinks".
    '''
    def __init__(self, prefix, sinkName):
        self.prefix = prefix
        self.sinkName = sinkName
        self.streamUrl = None
        self.streamName = None
        self.lastTtsMessage = None

    def isActive(self):
        '''
        Return true if the the chromecast is playing something.

        :param str castItemPrefix: the chrome cast item name
        '''
        return scope.items[self.prefix + "Idling"] == scope.OnOffType.OFF \
            and scope.items[self.getPlayerName()] == scope.PlayPauseType.PLAY

    def hasTitle(self):
        '''
        :rtype: bool
        '''
        name = self.prefix + "Title"
        return scope.UnDefType.UNDEF != scope.items[name] \
            and scope.UnDefType.NULL != scope.items[name] \
            and scope.StringType('') != scope.items[name]

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

    def getStreamUrl(self):
        '''
        Returns the current stream Uri or None if no stream set.

        :rtype: str
        '''
        return self.streamUrl

    def getStreamName(self):
        '''
        Returns the current stream name or None if no stream set.

        :rtype: str
        '''
        return self.streamName

    def getLastTtsMessage(self):
        '''
        :rtype: str
        '''
        return self.lastTtsMessage

    def setStream(self, streamName, streamUrl):
        '''
        Associate a stream URI with this object.

        :param str streamUrl:
        :param str streamName:
        '''
        self.streamName = streamName
        self.streamUrl = streamUrl

    def _setLastTtsMessage(self, ttsMessage):
        '''
        Internal API to be used by the cast_manager to set the last TTS message.
        :param str ttsMessage:
        '''
        self.lastTtsMessage = ttsMessage
