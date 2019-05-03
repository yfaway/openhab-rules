import time

from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.layout_model import zone
reload(zone)
from aaa_modules.layout_model.zone import Zone, Level

from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.dimmer import Dimmer
from aaa_modules.layout_model.switch import Fan
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.switch import Light
from aaa_modules.layout_model.motion_sensor import MotionSensor

from aaa_modules.layout_model.device_test import DeviceTest

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

ILLUMINANCE_THRESHOLD_IN_LUX = 10
MOTION_SENSOR_SWITCH_NAME = 'TestMotionSensorName'
ITEMS = [SwitchItem('TestLightName'),
      SwitchItem('TestTimerName'),
      SwitchItem(MOTION_SENSOR_SWITCH_NAME),
      NumberItem('IlluminanceSensorName'),
      StringItem('AstroSensorName'),
      DimmerItem('TestDimmerName'),
      SwitchItem('TestFanName'),
    ]

# Unit tests for zone_manager.py.
class ZoneTest(DeviceTest):

    def setUp(self):
        super(ZoneTest, self).setUp()

        [self.lightItem, self.timerItem, self.motionSensorItem,
         self.illuminanceSensorItem, self.astroSensorItem, self.dimmerItem,
         self.fan] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light = Light(self.lightItem, self.timerItem)
        self.lightWithIlluminance = Light(self.lightItem, self.timerItem,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.motionSensor = MotionSensor(self.motionSensorItem)
        self.astroSensor = AstroSensor(self.astroSensorItem)
        self.dimmer = Dimmer(self.dimmerItem, self.timerItem, 100, "0-23:59")
        self.fan = Fan(self.lightItem, self.timerItem)

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)
                elif isinstance(item, SwitchItem):
                    item.setState(UndefState)

        return ITEMS

    def testZoneCtor_validParams_gettersReturnValidValues(self):
        zoneName = 'bed room'
        zone = Zone(zoneName, [self.light], Level.SECOND_FLOOR)
        self.assertEqual(zoneName, zone.getName())
        self.assertEqual(Level.SECOND_FLOOR, zone.getLevel())
        self.assertEqual(str(Level.SECOND_FLOOR) + '_' + zoneName, zone.getId())
        self.assertEqual(1, len(zone.getDevices()))

    def testContainsOpenHabItem_negativeValue_returnsFalse(self):
        zone = Zone('name', [self.light], Level.SECOND_FLOOR)
        self.assertFalse(zone.containsOpenHabItem('blahblah'))

    def testContainsOpenHabItem_validNameButWrongType_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertFalse(zone.containsOpenHabItem(
                    self.light.getItemName(), MotionSensor))

    def testContainsOpenHabItem_validNameWithNoTypeSpecified_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertTrue(zone.containsOpenHabItem(self.light.getItemName()))

    def testContainsOpenHabItem_validNameWithTypeSpecified_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertTrue(zone.containsOpenHabItem(
                    self.light.getItemName(), Light))

    def testAddDevice_validDevice_deviceAdded(self):
        zone = Zone('ff').addDevice(self.light)
        self.assertEqual(1, len(zone.getDevices()))

    def testRemoveDevice_validDevice_deviceRemoved(self):
        zone = Zone('ff', [self.light])
        self.assertEqual(1, len(zone.getDevices()))

        zone = zone.removeDevice(self.light)
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

    def testGetIlluminanceLevel_noSensor_returnsMinusOne(self):
        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor])
        self.assertEqual(-1, zone.getIlluminanceLevel())

    def testGetIlluminanceLevel_withSensor_returnsPositiveValue(self):
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor])
        self.assertEqual(ILLUMINANCE_THRESHOLD_IN_LUX, zone.getIlluminanceLevel())

    def testIsLightOnTime_noSensor_returnsNone(self):
        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor])
        self.assertEqual(None, zone.isLightOnTime())

    def testIsLightOnTime_withSensorIndicatesDayTime_returnsFalse(self):
        self.astroSensorItem.setState(StringType('MORNING'))
        zone = Zone('ff', [self.lightWithIlluminance, self.astroSensor])
        self.assertFalse(zone.isLightOnTime())

    def testIsLightOnTime_withSensorIndicatesEveningTime_returnsTrue(self):
        self.astroSensorItem.setState(StringType(AstroSensor.LIGHT_ON_TIMES[0]))
        zone = Zone('ff', [self.lightWithIlluminance, self.astroSensor])
        self.assertTrue(zone.isLightOnTime())

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

    def testOnMotionSensorTurnedOn_validItemNameNoIlluminanceSensor_turnsOnLight(self):
        self.assertFalse(self.light.isOn())

        zone = Zone('ff', [self.light, self.motionSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertTrue(self.light.isOn())

    def testOnMotionSensorTurnedOn_illuminanceAboveThreshold_returnsFalse(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX + 1))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertFalse(isProcessed)
        self.assertFalse(self.light.isOn())

    def testOnMotionSensorTurnedOn_illuminanceBelowThreshold_turnsOnLight(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertTrue(isProcessed)

        time.sleep(0.1)
        self.assertTrue(self.light.isOn())

    def testOnMotionSensorTurnedOn_notLightOnTime_returnsFalse(self):
        self.astroSensorItem.setState(StringType('MORNING'))

        zone = Zone('ff', [self.light, self.astroSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertFalse(isProcessed)

    def testOnMotionSensorTurnedOn_notLightOnTimeButIlluminanceBelowThreshold_turnsOnLight(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))
        self.astroSensorItem.setState(StringType('MORNING'))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor, self.astroSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertTrue(isProcessed)
        time.sleep(0.1)
        self.assertTrue(self.light.isOn())

    def testOnMotionSensorTurnedOn_lightOnTime_turnsOnLight(self):
        self.assertFalse(self.light.isOn())

        self.astroSensorItem.setState(StringType(AstroSensor.LIGHT_ON_TIMES[0]))
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])

        isProcessed = zone.onMotionSensorTurnedOn(scope.events,
                self.motionSensor.getItemName())
        self.assertTrue(isProcessed)
        time.sleep(0.1)
        self.assertTrue(self.light.isOn())

    def testStr_noParam_returnsNonEmptyString(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor, 
                self.illuminanceSensor, self.dimmer, self.fan])
        info = str(zone)

        self.assertTrue(len(info) > 0)
        # logger.info(info)

run_test(ZoneTest, logger) 
