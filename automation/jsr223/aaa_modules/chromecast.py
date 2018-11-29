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
    def __init__(self, prefix):
        self.prefix = prefix

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

    # Returns the name of the player item for this chromecast object.
    # @return string
    def getPlayerName(self):
        return self.prefix + "Player"
