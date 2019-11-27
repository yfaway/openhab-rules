import unittest
import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

#from aaa_modules.layout_model import motion_sensor
#reload(motion_sensor)
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

MOTION_SENSOR_SWITCH_NAME = 'MotionSensorName'

# Unit tests for motion_sensor.py.
class MotionSensorTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(MOTION_SENSOR_SWITCH_NAME)

        self.motionSensorItem = SwitchItem(MOTION_SENSOR_SWITCH_NAME)
        scope.itemRegistry.add(self.motionSensorItem)

        self.motionSensorItem.setState(scope.OnOffType.OFF)

        self.motionSensor = MotionSensor(self.motionSensorItem)

    def tearDown(self):
        scope.itemRegistry.remove(self.motionSensorItem.getName())

    def testIsOn_various_returnsExpected(self):
        scope.events.sendCommand(self.motionSensorItem.getName(), "ON")
        time.sleep(0.1)
        self.assertTrue(self.motionSensor.isOn())

        scope.events.sendCommand(self.motionSensorItem.getName(), "OFF")
        time.sleep(0.1)
        self.assertFalse(self.motionSensor.isOn())

    def testIsOccupied_various_returnsExpected(self):
        itemName = self.motionSensorItem.getName()

        scope.events.sendCommand(itemName, "ON")
        time.sleep(0.1)
        self.motionSensor.onMotionSensorTurnedOn(scope.events, itemName)
        self.assertTrue(self.motionSensor.isOccupied())

        scope.events.sendCommand(self.motionSensorItem.getName(), "OFF")
        time.sleep(0.1)
        self.assertTrue(self.motionSensor.isOccupied())

PE.runUnitTest(MotionSensorTest)
