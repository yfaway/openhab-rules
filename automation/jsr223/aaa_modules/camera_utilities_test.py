import unittest

#from aaa_modules import camera_utilities
#reload(camera_utilities)
from aaa_modules import camera_utilities
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

# Unit tests for camera_utilities.py.
class CameraUtilitiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def testRetrieveSnapshot(self):
        itemPrefix = 'FF_Porch_Camera'
        urls = camera_utilities.retrieveSnapshots(itemPrefix, 2)
        self.assertTrue(len(urls) > 0)

#PE.runUnitTest(CameraUtilitiesTest)
