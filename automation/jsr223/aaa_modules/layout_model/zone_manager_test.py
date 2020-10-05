from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.library.items import SwitchItem
from org.eclipse.smarthome.core.library.types import DecimalType

#from aaa_modules.layout_model import zone_manager
#reload(zone_manager)
from aaa_modules.layout_model.zone_manager import ZoneManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.device_test import DeviceTest
from aaa_modules.layout_model.zone import Zone, ZoneEvent
from aaa_modules.layout_model.devices.astro_sensor import AstroSensor
from aaa_modules.layout_model.devices.dimmer import Dimmer
from aaa_modules.layout_model.devices.switch import Fan, Light, Switch
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor

from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch

ILLUMINANCE_THRESHOLD_IN_LUX = 8

ITEMS = [SwitchItem('TestLightName'),
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

        [self.lightItem, self.motionSensorItem,
         self.illuminanceSensorItem, self.astroSensorItem, self.dimmerItem,
         self.fanItem] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light = Light(self.lightItem, 2,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.motionSensor = MotionSensor(self.motionSensorItem)
        self.astroSensor = AstroSensor(self.astroSensorItem)
        self.dimmer = Dimmer(self.dimmerItem, 2, 100, "0-23:59")
        self.fan = Fan(self.fanItem, 2)

        self.zm = ZoneManager()

    def tearDown(self):
        pass

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
        self.zm.addZone(zone1)
        self.assertEqual(1, len(self.zm.getZones()))

        zone2 = Zone('2f')
        self.zm.addZone(zone2)
        self.assertEqual(2, len(self.zm.getZones()))

    def testGetZoneById_validZoneId_returnValidZone(self):
        zone1 = Zone('ff')
        self.zm.addZone(zone1)

        zone2 = Zone('2f')
        self.zm.addZone(zone2)

        self.assertEqual(zone1.getName(),
                self.zm.getZoneById(zone1.getId()).getName())
        self.assertEqual(zone2.getName(),
                self.zm.getZoneById(zone2.getId()).getName())

    def testGetZoneById_invalidZoneId_returnNone(self):
        self.assertTrue(None == self.zm.getZoneById('invalid zone id'))

    def testRemoveZone_validZone_zoneRemoved(self):
        zone1 = Zone('ff')
        self.zm.addZone(zone1)

        zone2 = Zone('2f')
        self.zm.addZone(zone2)

        self.assertEqual(2, len(self.zm.getZones()))

        self.zm.removeZone(zone1)
        self.assertEqual(1, len(self.zm.getZones()))

        self.zm.removeZone(zone2)
        self.assertEqual(0, len(self.zm.getZones()))

    def testGetDevicesByType_variousScenarios_returnsCorrectList(self):
        zone1 = Zone('ff').addDevice(self.light)
        zone2 = Zone('sf').addDevice(self.fan)

        self.zm.addZone(zone1)
        self.zm.addZone(zone2)
        self.assertEqual(2, len(self.zm.getZones()))

        self.assertEqual(1, len(self.zm.getDevicesByType(Light)))
        self.assertEqual(2, len(self.zm.getDevicesByType(Switch)))

        self.assertEqual(0, len(self.zm.getDevicesByType(AstroSensor)))

    def testOnMotionSensorTurnedOn_noZone_returnsFalse(self):
        self.assertFalse(self.zm.dispatchEvent(ZoneEvent.MOTION, 
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnMotionSensorTurnedOn_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertFalse(self.zm.dispatchEvent(ZoneEvent.MOTION, 
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnMotionSensorTurnedOn_withApplicableZone_returnsTrue(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        zone = Zone('ff', [self.light, self.motionSensor, self.illuminanceSensor])
        zone = zone.addAction(TurnOnSwitch())
        self.zm.addZone(zone)

        self.assertTrue(self.zm.dispatchEvent(ZoneEvent.MOTION, 
                    scope.events, self.motionSensor.getItem()))

    def testOnTimerExpired_noZone_returnsFalse(self):
        self.assertFalse(self.zm.onTimerExpired(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnTimerExpired_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertFalse(self.zm.onTimerExpired(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnSwitchTurnedOn_noZone_returnsFalse(self):
        self.assertFalse(self.zm.onSwitchTurnedOn(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnSwitchTurnedOn_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertFalse(self.zm.onSwitchTurnedOn(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnSwitchTurnedOn_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertTrue(self.zm.onSwitchTurnedOn(
                    scope.events, self.light.getItem()))

    def testOnSwitchTurnedOff_noZone_returnsFalse(self):
        self.assertFalse(self.zm.onSwitchTurnedOff(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnSwitchTurnedOff_withNonApplicableZone_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertFalse(self.zm.onSwitchTurnedOff(
                    scope.events, PE.createStringItem(INVALID_ITEM_NAME)))

    def testOnSwitchTurnedOff_withApplicableZone_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.zm.addZone(zone)

        self.assertTrue(self.zm.onSwitchTurnedOff(
                    scope.events, self.light.getItem()))

PE.runUnitTest(ZoneManagerTest)
