import unittest

from org.slf4j import Logger, LoggerFactory
from openhab.jsr223 import scope
from openhab.testing import run_test

from aaa_modules import camera_utilities
reload(camera_utilities)
from aaa_modules import camera_utilities

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for camera_utilities.py.
class CameraUtilitiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def testRetrieveSnapshot(self):
        itemPrefix = 'FF_Porch_Camera'
        urls = camera_utilities.retrieveSnapshots(itemPrefix, 2)
        self.assertTrue(len(urls) > 0)

# run_test(CameraUtilitiesTest, logger) 
