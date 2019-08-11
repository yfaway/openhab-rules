from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.layout_model import zone_manager
reload(zone_manager)
from aaa_modules.layout_model.zone_manager import ZoneManager

from aaa_modules.layout_model.device_test import DeviceTest
from aaa_modules.layout_model.zone import Zone
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.dimmer import Dimmer
from aaa_modules.layout_model.switch import Fan, Light, Switch
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

ITEMS = [SwitchItem('TestLightName'),
      SwitchItem('TestTimerName'),
      SwitchItem('TestMotionSensorName'),
      NumberItem('IlluminanceSensorName'),
      StringItem('AstroSensorName'),
      DimmerItem('TestDimmerName'),
      SwitchItem('TestFanName'),
    ]

INVALID_ITEM_NAME = 'invalid item name'

# Unit tests for zone_manager.py.
class ZoneManagerTest(DeviceTest):

    def setUp(self):
        super(ZoneManagerTest, self).setUp()

        [self.lightItem, self.timerItem, self.motionSensorItem,
         self.illuminanceSensorItem, self.astroSensorItem, self.dimmerItem,
         self.fanItem] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light = Light(self.lightItem, self.timerItem)
        self.motionSensor = MotionSensor(self.motionSensorItem)
        self.astroSensor = AstroSensor(self.astroSensorItem)
        self.dimmer = Dimmer(self.dimmerItem, self.timerItem, 100, "0-23:59")
        self.fan = Fan(self.fanItem, self.timerItem)

    def tearDown(self):
        ZoneManager.removeAllZones()

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)
                elif isinstance(item, SwitchItem):
                    item.setState(UndefState)

        return ITEMS

    def testAddZone_validZone_zoneAdded(self):
        zone1 = Zone('ff')
        ZoneManager.addZone(zone1)
        self.assertEqual(1, len(ZoneManager.getZones()))

        zone2 = Zone('2f')
        ZoneManager.addZone(zone2)
        self.assertEqual(2, len(ZoneManager.getZones()))

    def testGetZoneById_validZoneId_returnValidZone(self):
        zone1 = Zone('ff')
        ZoneManager.addZone(zone1)

        zone2 = Zone('2f')
        ZoneManager.addZone(zone2)

        self.assertEqual(zone1.getName(),
                ZoneManager.getZoneById(zone1.getId()).getName())
        self.assertEqual(zone2.getName(),
                ZoneManager.getZoneById(zone2.getId()).getName())

    def testGetZoneById_invalidZoneId_returnNone(self):
        self.assertTrue(None == ZoneManager.getZoneById('invalid zone id'))

    def testRemoveZone_validZone_zoneRemoved(self):
        zone1 = Zone('ff')
        ZoneManager.addZone(zone1)

        zone2 = Zone('2f')
        ZoneManager.addZone(zone2)

        self.assertEqual(2, len(ZoneManager.getZones()))

        ZoneManager.removeZone(zone1)
        self.assertEqual(1, len(ZoneManager.getZones()))

        ZoneManager.removeZone(zone2)
        self.assertEqual(0, len(ZoneManager.getZones()))

    def testGetDevicesByType_variousScenarios_returnsCorrectList(self):
        zone1 = Zone('ff').addDevice(self.light)
        zone2 = Zone('sf').addDevice(self.fan)

        ZoneManager.addZone(zone1)
        ZoneManager.addZone(zone2)
        self.assertEqual(2, len(ZoneManager.getZones()))

        self.assertEqual(1, len(ZoneManager.getDevicesByType(Light)))
        self.assertEqual(2, len(ZoneManager.getDevicesByType(Switch)))

        self.assertEqual(0, len(ZoneManager.getDevicesByType(AstroSensor)))

    def testOnMotionSensorTurnedOn_noZone_returnsFalse(self):
        self.assertFalse(ZoneManager.onMotionSensorTurnedOn(
                    scope.events, INVALID_ITEM_NAME))

    def testOnMotionSensorTurnedOn_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertFalse(ZoneManager.onMotionSensorTurnedOn(
                    scope.events, INVALID_ITEM_NAME))

    def testOnMotionSensorTurnedOn_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertTrue(ZoneManager.onMotionSensorTurnedOn(
                    scope.events, self.motionSensor.getItemName()))

    def testOnTimerExpired_noZone_returnsFalse(self):
        self.assertFalse(ZoneManager.onTimerExpired(
                    scope.events, INVALID_ITEM_NAME))

    def testOnTimerExpired_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertFalse(ZoneManager.onTimerExpired(
                    scope.events, INVALID_ITEM_NAME))

    def testOnTimerExpired_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertTrue(ZoneManager.onTimerExpired(
                    scope.events, self.timerItem.getName()))

    def testOnSwitchTurnedOn_noZone_returnsFalse(self):
        self.assertFalse(ZoneManager.onSwitchTurnedOn(
                    scope.events, INVALID_ITEM_NAME))

    def testOnSwitchTurnedOn_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertFalse(ZoneManager.onSwitchTurnedOn(
                    scope.events, INVALID_ITEM_NAME))

    def testOnSwitchTurnedOn_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertTrue(ZoneManager.onSwitchTurnedOn(
                    scope.events, self.light.getItemName()))

    def testOnSwitchTurnedOff_noZone_returnsFalse(self):
        self.assertFalse(ZoneManager.onSwitchTurnedOff(
                    scope.events, INVALID_ITEM_NAME))

    def testOnSwitchTurnedOff_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertFalse(ZoneManager.onSwitchTurnedOff(
                    scope.events, INVALID_ITEM_NAME))

    def testOnSwitchTurnedOff_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        ZoneManager.addZone(zone)

        self.assertTrue(ZoneManager.onSwitchTurnedOff(
                    scope.events, self.light.getItemName()))


run_test(ZoneManagerTest, logger) 
