from datetime import datetime, timedelta
import io
import os.path
import time

from core.jsr223 import scope

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

# The location to store snapshot images
_SNAPSHOT_PATH = '/tmp'

_WAIT_TIME_AFTER_FORCE_IMAGE_UPDATE_IN_SECONDS = 2

def retrieveSnapshotsFromFileSystem(
        maxNumberOfSeconds = 15,
        offsetSeconds = 5,
        epochSeconds = time.time(),
        camera = 'Camera1',
        imageLocation = '/home/pi/motion-os'):

    '''
    Retrieve the still camera images from the specified folder. The image files
    must be in this folder structure:
        {year}-{month}-{day}/{hour}-{minute}-{sec}
    Example: 2019-11-06/22-54-02.jpg.
    If any of the field is less than 10, then it must be padded by '0'. These
    are the structures written out by MotionEyeOS.

    :param int maxNumberOfSeconds: the maximum # of seconds to retrieve the
        images for
    :param int offsetSeconds: the # of seconds before the epochSeconds to
        retrieve the images for
    :param str camera: the name of the camera
    :param int epochSeconds: the time the motion triggered time
    :return: list of snapshot URLs or empty list if there is no snapshot
    :rtype: list(str)
    '''

    pad = lambda x: "0{}".format(x) if x < 10 else x

    urls = []

    if imageLocation.endswith('/'):
        imageLocation = imageLocation[:-1]

    currentTime = datetime.fromtimestamp(epochSeconds)
    path = "{}/{}/{}-{}-{}".format(imageLocation, camera, currentTime.year,
            currentTime.month, pad(currentTime.day))

    for second in range(-offsetSeconds, maxNumberOfSeconds - offsetSeconds):
        delta = timedelta(seconds = second)
        instant = currentTime + delta
        fileName = "{}-{}-{}.jpg".format(pad(instant.hour),
                pad(instant.minute), pad(instant.second))
        pathAndFilename = "{}/{}".format(path, fileName)

        if os.path.exists(pathAndFilename):
            url = "file://{}".format(pathAndFilename)
            urls.append(url)

    return urls

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

    PE.logInfo('Retrieving {} snapshots'.format(snapshotCount))
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
