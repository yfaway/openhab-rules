# Represents a Chromecast, Chromecast Audio, or a Google Home device.

from org.slf4j import Logger, LoggerFactory
from openhab.jsr223 import scope

LOG = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class ChromeCast:
    # Ctor.
    # @param prefix string the item name prefix, as defined in the .item
    #     file. By convention, other channels of this device will have this
    #     naming pattern: {prefix}Idling, {prefix}Title, {prefix}Player, and
    #     so on.
    # @param sink the sink name for voice and audio play. The sink name can be
    #     retrieved by running "openhab-cli console" and then 
    #     "smarthome:audio sinks".
    def __init__(self, prefix, sink):
        self.prefix = prefix
        self.sink = sink

    # Return true if the the chromecast is playing something.
    # @param castItemPrefix string the chrome cast item name
    def isActive(self):
        return scope.items[self.prefix + "Idling"] == scope.OnOffType.OFF \
            and scope.items[self.getPlayerName()] == scope.PlayPauseType.PLAY

    def hasTitle(self):
        name = self.prefix + "Title"
        return scope.UnDefType.UNDEF != scope.items[name] \
            and scope.UnDefType.NULL != scope.items[name] \
            and scope.StringType('') != scope.items[name]

    def getPrefix(self):
        return self.prefix

    # Returns the name of the player item for this chromecast object.
    # @return string
    def getPlayerName(self):
        return self.prefix + "Player"

    # Return the sink name for Voice.say and Audio.playStream usages.
    def getSinkName(self):
        return self.sink
