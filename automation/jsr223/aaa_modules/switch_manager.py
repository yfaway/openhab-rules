# Contains utility methods that operate on DimmerItem or SwitchItem. These
# items might control lights or fans.

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.joda.time import DateTime

from openhab.jsr223 import scope

GROUP_FIRST_FLOOR_LIGHT_SWITCH = "gFirstFloorLightSwitch"
GROUP_SECOND_FLOOR_LIGHT_SWITCH = "gSecondFloorLightSwitch"

_LOG = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Change the state of all first floor lights.
# @param state string 'ON' or 'OFF'
def changeFirstFloorLightsTo(state):
    _changeLightGroupStateTo(GROUP_FIRST_FLOOR_LIGHT_SWITCH, state)

# Change the state of all first floor lights.
# @param state string 'ON' or 'OFF'
def changeSecondFloorLightsTo(state):
    _changeLightGroupStateTo(GROUP_SECOND_FLOOR_LIGHT_SWITCH, state)

# Change the state of the Foyer light.
# @param state string 'ON' or 'OFF'
def changeFoyerLightTo(state):
    scope.events.sendCommand('FF_Foyer_LightSwitch', state)

def isAnyFirstFloorLightOn():
    return scope.items[GROUP_FIRST_FLOOR_LIGHT_SWITCH] == scope.OnOffType.ON

def isAnySecondFloorLightOn():
    return scope.items[GROUP_SECOND_FLOOR_LIGHT_SWITCH] == scope.OnOffType.ON

# Returns true if a switch is on.
# @param switchItem can be a regular OnOffItem or a DimmerItem. In the later
#     case, the dimmer switch is considered on if its value is greater than 0.
def isSwitchOn(switchItem):
    return (switchItem.state == scope.OnOffType.ON) \
        or (isinstance(switchItem, DimmerItem)
            and scope.UnDefType.NULL != switchItem.state
            and scope.UnDefType.UNDEF != switchItem.state 
            and switchItem.state > scope.DecimalType(0))

# Change all the lights in the given group to the given state.
# @param group string
# @param state string 'ON' or 'OFF'
def _changeLightGroupStateTo(group, state):
    scope.events.sendCommand(group, state)
