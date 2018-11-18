from org.slf4j import Logger, LoggerFactory
from openhab.rules import rule
from openhab.triggers import when
import constants

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Turn off all lights when armed away")
@when("Item PARTITION1_ARM_MODE changed to 1")
def turnOffAllLights(event):
    events.sendCommand(constants.GROUP_LIGHT_SWITCHS, "OFF")
