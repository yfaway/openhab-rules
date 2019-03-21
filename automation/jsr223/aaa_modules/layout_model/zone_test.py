import unittest
import time

from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.layout_model import zone
reload(zone)
from aaa_modules.layout_model.zone import Zone

from aaa_modules.layout_model.switch import Light
from aaa_modules.layout_model.dimmer import Dimmer

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

LIGHT_SWITCH_NAME = 'TestLightName'
TIMER_NAME = 'TestTimerName'

# Unit tests for zone_manager.py.
class ZoneTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(LIGHT_SWITCH_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.lightItem = SwitchItem(LIGHT_SWITCH_NAME)
        scope.itemRegistry.add(self.lightItem)

        self.timerItem = SwitchItem(TIMER_NAME)
        scope.itemRegistry.add(self.timerItem)

        self.lightItem.setState(scope.OnOffType.OFF)
        self.timerItem.setState(scope.OnOffType.OFF)

        self.light = Light(self.lightItem, self.timerItem)

    def tearDown(self):
        scope.itemRegistry.remove(self.lightItem.getName())
        scope.itemRegistry.remove(self.timerItem.getName())

    def testAddDevice_validDevice_deviceAdded(self):
        zone = Zone('ff')
        zone.addDevice(self.light)
        self.assertEqual(1, len(zone.getDevices()))

    def testRemoveDevice_validDevice_deviceRemoved(self):
        zone = Zone('ff', [self.light])
        self.assertEqual(1, len(zone.getDevices()))

        zone.removeDevice(self.light)
        self.assertEqual(0, len(zone.getDevices()))

    def testGetDevicesByType_validType_deviceRemoved(self):
        zone = Zone('ff', [self.light])
        self.assertEqual(1, len(zone.getDevicesByType(Light)))
        self.assertEqual(0, len(zone.getDevicesByType(Dimmer)))

    def testOnTimerExpired_validTimerItem_returnsTrue(self):

        self.lightItem.setState(scope.OnOffType.ON)
        self.timerItem.setState(scope.OnOffType.ON)
        time.sleep(0.1)

        zone = Zone('ff', [self.light])

        isProcessed = zone.onTimerExpired(scope.events, self.timerItem.getName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertEqual(scope.OnOffType.OFF, self.lightItem.getState())
        self.assertEqual(scope.OnOffType.OFF, self.timerItem.getState())

    def testOnTimerExpired_invalidTimerItem_returnsFalse(self):
        zone = Zone('ff', [self.light])

        isProcessed = zone.onTimerExpired(scope.events, 'dummy name')
        self.assertFalse(isProcessed)



run_test(ZoneTest, logger) 
