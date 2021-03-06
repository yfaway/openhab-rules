import time

from core.rules import rule
from core.triggers import when

from aaa_modules import cast_manager
from aaa_modules import switch_manager

@rule("Say the first notice")
@when("Time cron 0 45 19 ? * MON-THU,SUN *")
def sayFirstNotice(event):
    if switch_manager.isAnyFirstFloorLightOn():
        cast_manager.playMessage(createMessageWithTime(
                    'Kids, it is {}:{}; please put away everything and prepare to go upstairs.'),
                cast_manager.getFirstFloorCasts())

@rule("Say the second notice and turn off the lights")
@when("Time cron 0 50 19 ? * MON-THU,SUN *")
def saySecondNotice(event):
    if switch_manager.isAnyFirstFloorLightOn():
        cast_manager.playMessage(createMessageWithTime(
                    'Kids, it is {}:{}; please go upstairs now.'),
                cast_manager.getFirstFloorCasts())
        switch_manager.changeFirstFloorLightsTo('OFF')
        time.sleep(2)
        switch_manager.changeFoyerLightTo('ON')

# String format two values with the current hour and minute.
# @param message string
# @return string
def createMessageWithTime(message):
    timeStruct = time.localtime()
    hourOfDay = timeStruct[3]
    minute = timeStruct[4]

    if hourOfDay > 12:
        hourOfDay -= 12

    return message.format(hourOfDay, minute)
