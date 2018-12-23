import unittest

from org.slf4j import Logger, LoggerFactory
from openhab.jsr223 import scope
from openhab.testing import run_test

import camera
reload(camera)
import camera

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for camera.py.
class CameraRuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        camera.items = scope.items
        camera.events = scope.events
        camera.OnOffType = scope.OnOffType

    def testRetrieveSnapshot(self):
        itemPrefix = 'FF_Porch_Camera'
        urls = camera.retrieveSnapshots(itemPrefix, 2)
        self.assertTrue(len(urls) > 0)

#run_test(CameraRuleTest, logger) 
