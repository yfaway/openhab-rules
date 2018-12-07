# Controls the Ecobee thermostat.

from org.slf4j import Logger, LoggerFactory
from openhab.actions import EcobeeAction
from openhab.rules import rule
from openhab.triggers import when
from org.joda.time import DateTime

from aaa_modules import security_manager
reload(security_manager)
from aaa_modules import security_manager

ECOBEE_ID = '411921197263'

ITEM_DESIRED_HEAT = 'FF_GreatRoom_Thermostat_DesiredHeat'
ITEM_DESIRED_COOL = 'FF_GreatRoom_Thermostat_DesiredCool'

_HOLD_FAN_PARAMS = {'fan': 'on',
          'isTemperatureAbsolute': False,
          'isTemperatureRelative': False,
          'coolHoldTemp': items[ITEM_DESIRED_COOL].floatValue(),
          'heatHoldTemp': items[ITEM_DESIRED_HEAT].floatValue(),
          'isCoolOff': True,
          'isHeatOff': True, }

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Turn off fan when armed away")
@when(security_manager.WHEN_CHANGED_TO_ARMED_AWAY)
def resume(event):
    log.info("[thermostat] turn off fan")
    EcobeeAction.ecobeeResumeProgram(ECOBEE_ID, True)

@rule("Turn on fan when unarmed and is in winter")
@when(security_manager.WHEN_CHANGED_FROM_ARM_AWAY_TO_UNARMED)
def holdFanOn(event):
    if isInWinter():
        log.info("[thermostat] turn on fan")
        EcobeeAction.ecobeeSetHold(ECOBEE_ID, _HOLD_FAN_PARAMS, None, None, None, None)

def isInWinter():
    month = DateTime.now().getMonthOfYear()
    return month == 12 or month < 5
