import io
import time

from org.slf4j import Logger, LoggerFactory
from openhab import osgi
from openhab.rules import rule
from openhab.triggers import when
from openhab.actions import Mail

# Allowed threshold in seconds between handling of the motion alarm.
_INTERVAL_IN_SECONDS = 30

# The maximum number of snapshots to capture when a motion alarm is triggered.
_SNAPSHOT_COUNT = 5

# The location to store snapshot images
_SNAPSHOT_PATH = '/tmp'

_WAIT_TIME_AFTER_FORCE_IMAGE_UPDATE_IN_SECONDS = 2

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

    attachmentUrls = retrieveSnapshots(prefix, _SNAPSHOT_COUNT)

    logger.info('Sending camera snapshot with {} images'.format(
                len(attachmentUrls)))
    # Mail.sendMail(emailAddress, 'Cam image', '', attachmentUrls)

# Retrieve {@link _SNAPSHOT_COUNT} snapshots.
# @param itemPrefix stirng the camera item prefix; the items Image and
#     UpdateImage are created from the prefix.
# @param snapshotCount int
# @return list of snapshot URLs
def retrieveSnapshots(itemPrefix, snapshotCount):
    attachmentUrls = []

    imageItemName = itemPrefix + '_Image'
    updateItemName = itemPrefix + '_UpdateImage'

    previousRawBytes = []
    for idx in range(snapshotCount):
        logger.info('Retrieving snapshot {}'.format(idx))

        # Flip the state of the update channel to force retrieval of new image
        if items[updateItemName] == OnOffType.ON:
            events.sendCommand(updateItemName, "OFF")
        else:
            events.sendCommand(updateItemName, "ON")

        time.sleep(_WAIT_TIME_AFTER_FORCE_IMAGE_UPDATE_IN_SECONDS)

        rawBytes = items[imageItemName].getBytes()
        if rawBytes != previousRawBytes:
            fileName = '{}/{}-{}.jpg'.format(_SNAPSHOT_PATH, itemPrefix, idx)
            file = io.open(fileName, 'wb')
            file.write(rawBytes)
            file.close()

            attachmentUrls.append('file://' + fileName)

            previousRawBytes = rawBytes

    return attachmentUrls
