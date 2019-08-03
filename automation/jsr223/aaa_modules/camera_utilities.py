import io
import time
from org.slf4j import Logger, LoggerFactory
from core.jsr223 import scope

# The location to store snapshot images
_SNAPSHOT_PATH = '/tmp'

_WAIT_TIME_AFTER_FORCE_IMAGE_UPDATE_IN_SECONDS = 2

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

def retrieveSnapshots(itemPrefix, snapshotCount):
    '''
    Retrieve the supplied number of snapshots.

    :param str itemPrefix: the camera item prefix; the items Image and\
    UpdateImage are created from the prefix.
    :param int snapshotCount: the # of snapshot images to retrieve
    :return: list of snapshot URLs
    :rtype: list(str)
    '''
    attachmentUrls = []

    imageItemName = itemPrefix + '_Image'
    updateItemName = itemPrefix + '_UpdateImage'

    logger.info('Retrieving {} snapshots'.format(snapshotCount))
    previousRawBytes = []
    for idx in range(snapshotCount):
        # Flip the state of the update channel to force retrieval of new image
        if scope.items[updateItemName] == scope.OnOffType.ON:
            scope.events.sendCommand(updateItemName, "OFF")
        else:
            scope.events.sendCommand(updateItemName, "ON")

        time.sleep(_WAIT_TIME_AFTER_FORCE_IMAGE_UPDATE_IN_SECONDS)

        imageState = scope.items[imageItemName]
        if scope.UnDefType.UNDEF != imageState and scope.UnDefType.NULL != imageState:
            rawBytes = imageState.getBytes()
            if rawBytes != previousRawBytes:
                fileName = '{}/{}-{}.jpg'.format(_SNAPSHOT_PATH, itemPrefix, idx)
                file = io.open(fileName, 'wb')
                file.write(rawBytes)
                file.close()

                attachmentUrls.append('file://' + fileName)

                previousRawBytes = rawBytes

    return attachmentUrls
