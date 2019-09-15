# Controls the Ecobee thermostat.

from org.slf4j import Logger, LoggerFactory
from core.actions import EcobeeAction
from core.rules import rule
from core.triggers import when
from org.joda.time import DateTime

from aaa_modules import security_manager

ECOBEE_ID = '411921197263'

_ITEM_DESIRED_HEAT = 'FF_GreatRoom_Thermostat_DesiredHeat'
_ITEM_DESIRED_COOL = 'FF_GreatRoom_Thermostat_DesiredCool'

_HOLD_FAN_PARAMS = {'fan': 'on',
          'isTemperatureAbsolute': False,
          'isTemperatureRelative': False,
          'coolHoldTemp': items[_ITEM_DESIRED_COOL].floatValue(),
          'heatHoldTemp': items[_ITEM_DESIRED_HEAT].floatValue(),
          'isCoolOff': True,
          'isHeatOff': True, }

_AWAY_CLIMATE_REF = 'away'

log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Turn off fan when armed away")
@when(security_manager.WHEN_CHANGED_TO_ARMED_AWAY)
def resume(event):
    if not security_manager.isInVacation(items):
        EcobeeAction.ecobeeSetHold(ECOBEE_ID, None, None, _AWAY_CLIMATE_REF, None,
                None, None, None)
        log.info("[Thermostat] Changed to Away mode")

@rule("Turn on fan when unarmed and is in winter")
@when(security_manager.WHEN_CHANGED_FROM_ARM_AWAY_TO_UNARMED)
def holdFanOn(event):
    if not security_manager.isInVacation(items):
        EcobeeAction.ecobeeResumeProgram(ECOBEE_ID, True)
        log.info("[Thermostat] Resumed normal schedule")

        if isInWinter():
            EcobeeAction.ecobeeSetHold(ECOBEE_ID, _HOLD_FAN_PARAMS, None, None, None, None)
            log.info("[Thermostat] Turned on fan")

def isInWinter():
    month = DateTime.now().getMonthOfYear()
    return month == 12 or month < 5
