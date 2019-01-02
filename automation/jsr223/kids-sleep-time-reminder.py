from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

from aaa_modules import switch_manager
reload(switch_manager)
from aaa_modules import switch_manager

from org.slf4j import Logger, LoggerFactory
log = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

@rule("Say the first notice")
@when("Time cron 0 30 20 1/1 * ? *")
def sayFirstNotice(event):
    if switch_manager.isAnyFirstFloorLightOn():
        cast_manager.playMessage('Kids, it is 8:30; please put away everything and prepare to go upstairs.',
                cast_manager.getFirstFloorCasts())

@rule("Say the second notice and turn off the lights")
@when("Time cron 0 45 20 1/1 * ? *")
def saySecondNotice(event):
    if switch_manager.isAnyFirstFloorLightOn():
        cast_manager.playMessage('Kids, it is 8:45; please go upstairs now.',
                cast_manager.getFirstFloorCasts())
        switch_manager.changeFirstFloorLightsTo('OFF')
        switch_manager.changeFoyerLightTo('ON')
