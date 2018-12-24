import time

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from openhab.actions import Mail

from aaa_modules import camera_utilities
reload(camera_utilities)
from aaa_modules import camera_utilities

# Allowed threshold in seconds between handling of the motion alarm.
_INTERVAL_IN_SECONDS = 30

# The maximum number of snapshots to capture when a motion alarm is triggered.
_SNAPSHOT_COUNT = 5

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Track the last motion alarm event for each camera; itemPrefix -> int.
lastMotionEvents = {}

@rule("Send snapshot images")
@when("Member of gCameraMotionAlarm changed to ON")
def sendSnapshot(event):
    global lastMotionEvents

    localIdx = event.itemName.rfind("_MotionAlarm")
    prefix = event.itemName[:localIdx]

    if prefix in lastMotionEvents:
        timestamp = lastMotionEvents[prefix]
        if (time.time() - timestamp <= _INTERVAL_IN_SECONDS):
            logger.info('[{}] Ignore event; too close to previous event.'.format(
                        prefix))
            return

    lastMotionEvents[prefix] = time.time()

    attachmentUrls = camera_utilities.retrieveSnapshots(prefix, _SNAPSHOT_COUNT)

    logger.info('Sending camera snapshot with {} images'.format(
                len(attachmentUrls)))
    # Mail.sendMail(emailAddress, '[{}] Camera motion alarm triggered'.format(prefix), '', attachmentUrls)
