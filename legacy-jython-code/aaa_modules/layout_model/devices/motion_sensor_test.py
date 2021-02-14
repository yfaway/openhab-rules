import unittest

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

#from aaa_modules.layout_model.devices import motion_sensor
#reload(motion_sensor)
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor
from aaa_modules.layout_model.device_test import MockedEventDispatcher

MOTION_SENSOR_SWITCH_NAME = 'MotionSensorName'

# Unit tests for motion_sensor.py.
class MotionSensorTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(MOTION_SENSOR_SWITCH_NAME)

        self.motionSensorItem = SwitchItem(MOTION_SENSOR_SWITCH_NAME)
        scope.itemRegistry.add(self.motionSensorItem)

        self.motionSensorItem.setState(scope.OnOffType.OFF)

        self.motionSensor = MotionSensor(self.motionSensorItem)

        self.events = MockedEventDispatcher(scope.itemRegistry)

    def tearDown(self):
        scope.itemRegistry.remove(self.motionSensorItem.getName())

    def testIsOn_various_returnsExpected(self):
        self.events.sendCommand(self.motionSensorItem.getName(), "ON")
        self.assertTrue(self.motionSensor.isOn())

        self.events.sendCommand(self.motionSensorItem.getName(), "OFF")
        self.assertFalse(self.motionSensor.isOn())

    def testIsOccupied_various_returnsExpected(self):
        itemName = self.motionSensorItem.getName()

        self.events.sendCommand(itemName, "ON")
        self.motionSensor.onMotionSensorTurnedOn(self.events, itemName)
        self.assertTrue(self.motionSensor.isOccupied())

        self.events.sendCommand(self.motionSensorItem.getName(), "OFF")
        self.assertTrue(self.motionSensor.isOccupied())

PE.runUnitTest(MotionSensorTest)
