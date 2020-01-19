import time

from core import osgi
from core.rules import rule
from core.triggers import when

from aaa_modules import camera_utilities
from aaa_modules.alert import *
from aaa_modules.alert_manager import *

# Allowed threshold in seconds between handling of the motion alarm.
_INTERVAL_IN_SECONDS = 60

# The maximum number of snapshots to capture when a motion alarm is triggered.
_SNAPSHOT_COUNT = 5

# Track the last motion alarm event for each camera; itemPrefix -> int.
lastMotionEvents = {}

#@rule("Send snapshot images")
#@when("Member of gCameraMotionAlarm changed to ON")
def sendSnapshot(event):
    global lastMotionEvents

    localIdx = event.itemName.rfind("_MotionAlarm")
    prefix = event.itemName[:localIdx]

    if prefix in lastMotionEvents:
        timestamp = lastMotionEvents[prefix]
        if (time.time() - timestamp <= _INTERVAL_IN_SECONDS):
            PE.logInfo('[{}] Ignore event; too close to previous event.'.format(
                        prefix))
            return

    lastMotionEvents[prefix] = time.time()

    attachmentUrls = camera_utilities.retrieveSnapshots(prefix, _SNAPSHOT_COUNT)

    PE.logInfo('Sending camera snapshot with {} images'.format(
                len(attachmentUrls)))
    
    # todo: use warning instead of info for evening hours.
    alert = Alert.createInfoAlert('[{}] Camera motion alarm triggered'.format(prefix),
            None, attachmentUrls)
    # result = AlertManager.processAlert(alert)
    # if not result:
    #     PE.logInfo('Failed to send camera snapshots')

