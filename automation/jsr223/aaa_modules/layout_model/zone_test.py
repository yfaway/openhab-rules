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
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.dimmer import Dimmer

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

LIGHT_SWITCH_NAME = 'TestLightName'
MOTION_SENSOR_SWITCH_NAME = 'TestMotionSensorName'
TIMER_NAME = 'TestTimerName'

# Unit tests for zone_manager.py.
class ZoneTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(MOTION_SENSOR_SWITCH_NAME)
        scope.itemRegistry.remove(LIGHT_SWITCH_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.lightItem = SwitchItem(LIGHT_SWITCH_NAME)
        scope.itemRegistry.add(self.lightItem)

        self.motionSensorItem = SwitchItem(MOTION_SENSOR_SWITCH_NAME)
        scope.itemRegistry.add(self.motionSensorItem)

        self.timerItem = SwitchItem(TIMER_NAME)
        scope.itemRegistry.add(self.timerItem)

        self.motionSensorItem.setState(scope.OnOffType.OFF)
        self.lightItem.setState(scope.OnOffType.OFF)
        self.timerItem.setState(scope.OnOffType.OFF)

        self.light = Light(self.lightItem, self.timerItem)
        self.motionSensor = MotionSensor(self.motionSensorItem)

    def tearDown(self):
        scope.itemRegistry.remove(self.timerItem.getName())
        scope.itemRegistry.remove(self.motionSensorItem.getName())
        scope.itemRegistry.remove(self.lightItem.getName())

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

    def testIsOccupied_everythingOff_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.assertFalse(zone.isOccupied())

    def testIsOccupied_switchIsOn_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.light.turnOn(scope.events)
        time.sleep(0.1)

        self.assertTrue(zone.isOccupied())

    def testIsOccupied_motionEventTriggeredButLightIsOff_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.motionSensor.onMotionSensorTurnedOn(
                scope.events, MOTION_SENSOR_SWITCH_NAME)
        time.sleep(0.1)

        self.light.turnOff(scope.events)
        time.sleep(0.1)

        self.assertTrue(zone.isOccupied())

    def testOnTimerExpired_validTimerItem_returnsTrue(self):

        self.lightItem.setState(scope.OnOffType.ON)
        self.timerItem.setState(scope.OnOffType.ON)
        time.sleep(0.1)

        zone = Zone('ff', [self.light])

        isProcessed = zone.onTimerExpired(scope.events, self.timerItem.getName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertEqual(scope.OnOffType.OFF, self.lightItem.getState())

    def testOnTimerExpired_invalidTimerItem_returnsFalse(self):
        zone = Zone('ff', [self.light])

        isProcessed = zone.onTimerExpired(scope.events, 'dummy name')
        self.assertFalse(isProcessed)

    def testOnSwitchedTurnedOn_validItemName_returnsTrue(self):
        self.timerItem.setState(scope.OnOffType.OFF)

        zone = Zone('ff', [self.light])

        isProcessed = zone.onSwitchTurnedOn(scope.events, self.lightItem.getName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testOnSwitchedTurnedOff_validItemName_returnsTrue(self):
        self.timerItem.setState(scope.OnOffType.ON)

        zone = Zone('ff', [self.light])

        isProcessed = zone.onSwitchTurnedOff(scope.events, self.lightItem.getName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertEqual(scope.OnOffType.OFF, self.timerItem.getState())

    def testOnMotionSensorTurnedOn_validItemName_returnsTrue(self):
        self.assertFalse(self.light.isOn())

        zone = Zone('ff', [self.light, self.motionSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getSwitchItem().getName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertTrue(self.light.isOn())

run_test(ZoneTest, logger) 
