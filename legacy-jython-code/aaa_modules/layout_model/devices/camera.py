import time

from aaa_modules.camera_utilities import retrieveSnapshotsFromFileSystem
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class Camera(Device):
    '''
    Represents a network camera.
    '''

    def __init__(self, cameraNameItem, cameraName,
            imageLocation = '/home/pi/motion-os'):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.StringItem cameraNameItem: \
            a dummy item; won't be used by this device.
        :param string cameraName the optional file location of the still images
        :param string imageLocation the optional file location of the still images
        :raise ValueError: if cameraNameItem is invalid
        '''
        Device.__init__(self, cameraNameItem)

        self._cameraName = cameraName
        self._imageLocation = imageLocation

    def hasMotionEvent(self):
        '''
        Sleep for 10 seconds to wait for the images to be flushed to the file
        system. After that, check to see if there is any snapshot. If yes,
        return true.
        :rtype: bool
        '''
        currentEpoch = time.time()
        time.sleep(10)
        urls = self.getSnapshotUrls(currentEpoch, 6, 5)
        return len(urls) > 0

    def getSnapshotUrls(self, timeInEpochSeconds = time.time(),
            maxNumberOfSeconds = 15, offsetSeconds = 5):
        '''
        Retrieve the still camera image URLs.
        :param int timeInEpochSeconds: the pivot time to calcualte the start
            and end times for the still images.
        :param int maxNumberOfSeconds: the maximum # of seconds to retrieve the
            images for
        :param int offsetSeconds: the # of seconds before the epochSeconds to
            retrieve the images for
        :return: list of snapshot URLs or empty list if there is no snapshot
        :rtype: list(str)
        '''
        return retrieveSnapshotsFromFileSystem(
                maxNumberOfSeconds, offsetSeconds, timeInEpochSeconds,
                self._cameraName, self._imageLocation)

