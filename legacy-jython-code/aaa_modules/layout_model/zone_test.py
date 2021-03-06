from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.library.items import SwitchItem
from org.eclipse.smarthome.core.library.types import DecimalType
from org.eclipse.smarthome.core.library.types import OnOffType
from org.eclipse.smarthome.core.library.types import StringType

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.mocked_zone_manager import MockedZoneManager
#from aaa_modules.layout_model import zone
#reload(zone)
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.event_info import EventInfo

from aaa_modules.layout_model.devices.astro_sensor import AstroSensor
from aaa_modules.layout_model.devices.dimmer import Dimmer
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor
from aaa_modules.layout_model.devices.plug import Plug
from aaa_modules.layout_model.devices.switch import Fan, Light

from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

from aaa_modules.layout_model.device_test import DeviceTest

ILLUMINANCE_THRESHOLD_IN_LUX = 10
MOTION_SENSOR_SWITCH_NAME = 'TestMotionSensorName'
ITEMS = [SwitchItem('TestLightName'),
      SwitchItem(MOTION_SENSOR_SWITCH_NAME),
      NumberItem('IlluminanceSensorName'),
      StringItem('AstroSensorName'),
      DimmerItem('TestDimmerName'),
      SwitchItem('TestFanName'),
      SwitchItem('TestPlug'),
      NumberItem('TestPlugPower'),
    ]

# Unit tests for zone_manager.py.
class ZoneTest(DeviceTest):

    def setUp(self):
        super(ZoneTest, self).setUp()

        [self.lightItem, self.motionSensorItem,
         self.illuminanceSensorItem, self.astroSensorItem, self.dimmerItem,
         self.fanItem, self.plugItem, self.plugPowerItem] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light = Light(self.lightItem, 2)
        self.lightWithIlluminance = Light(self.lightItem, 2,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.motionSensor = MotionSensor(self.motionSensorItem)
        self.astroSensor = AstroSensor(self.astroSensorItem)
        self.dimmer = Dimmer(self.dimmerItem, 2, 100, "0-23:59")
        self.fan = Fan(self.lightItem, 2)

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

    def testCreateExternalZone_validParams_returnsAnExternalZone(self):
        zoneName = 'bed room'
        zone = Zone.createExternalZone(zoneName)
        self.assertEqual(zoneName, zone.getName())
        self.assertTrue(zone.isExternal())

    def testCreateFirstFloorZone_validParams_returnsAFirstFloorZone(self):
        zoneName = 'bed room'
        zone = Zone.createFirstFloorZone(zoneName)
        self.assertEqual(zoneName, zone.getName())
        self.assertEqual(Level.FIRST_FLOOR, zone.getLevel())
        self.assertFalse(zone.isExternal())

    def testCreateSecondFloorZone_validParams_returnsASecondFloorZone(self):
        zoneName = 'bed room'
        zone = Zone.createSecondFloorZone(zoneName)
        self.assertEqual(zoneName, zone.getName())
        self.assertEqual(Level.SECOND_FLOOR, zone.getLevel())
        self.assertFalse(zone.isExternal())

    def testContainsOpenHabItem_negativeValue_returnsFalse(self):
        zone = Zone('name', [self.light], Level.SECOND_FLOOR)
        self.assertFalse(zone.containsOpenHabItem(self.fanItem))

    def testContainsOpenHabItem_validNameButWrongType_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertFalse(zone.containsOpenHabItem(
                    self.lightItem, MotionSensor))

    def testContainsOpenHabItem_validNameWithNoTypeSpecified_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertTrue(zone.containsOpenHabItem(self.lightItem))

    def testContainsOpenHabItem_validNameWithTypeSpecified_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        self.assertTrue(zone.containsOpenHabItem(self.lightItem, Light))

    def testAddDevice_validDevice_deviceAdded(self):
        zone = Zone('ff').addDevice(self.light)
        self.assertEqual(1, len(zone.getDevices()))

    def testRemoveDevice_validDevice_deviceRemoved(self):
        zone = Zone('ff', [self.light])
        self.assertEqual(1, len(zone.getDevices()))

        zone = zone.removeDevice(self.light)
        self.assertEqual(0, len(zone.getDevices()))

    def testGetDevicesByType_validType_returnsExpectedDevices(self):
        zone = Zone('ff', [self.light])
        self.assertEqual(1, len(zone.getDevicesByType(Light)))
        self.assertEqual(0, len(zone.getDevicesByType(Dimmer)))

    def testGetDeviceByEvent_validEvent_returnsExpectedDevice(self):
        zone = Zone('ff', [self.light])

        eventInfo = EventInfo(ZoneEvent.MOTION, self.lightItem, zone,
                MockedZoneManager([zone]), self.getMockedEventDispatcher())
        self.assertEqual(self.light, zone.getDeviceByEvent(eventInfo))

    def testGetDeviceByEvent_invalidEvent_returnsNone(self):
        zone = Zone('ff', [self.light])

        eventInfo = EventInfo(ZoneEvent.MOTION, self.motionSensorItem, zone,
                MockedZoneManager([zone]), self.getMockedEventDispatcher())
        self.assertEqual(None, zone.getDeviceByEvent(eventInfo))

    def testAddAction_oneValidAction_actionAdded(self):
        zone = Zone('ff').addAction(TurnOnSwitch())
        self.assertEqual(1, len(zone.getActions(ZoneEvent.MOTION)))

        self.assertEqual(0, len(zone.getActions(ZoneEvent.SWITCH_TURNED_ON)))

    def testAddAction_twoValidAction_actionAdded(self):
        zone = Zone('ff').addAction(TurnOnSwitch())
        zone = zone.addAction(TurnOffAdjacentZones())
        self.assertEqual(1, len(zone.getActions(ZoneEvent.MOTION)))
        self.assertEqual(1, len(zone.getActions(ZoneEvent.SWITCH_TURNED_ON)))

    def testIsOccupied_everythingOff_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        (occupied, device) = zone.isOccupied()
        self.assertFalse(occupied)
        self.assertEqual(None, device)

    def testIsOccupied_switchIsOn_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.light.turnOn(self.getMockedEventDispatcher())

        (occupied, device) = zone.isOccupied()
        self.assertTrue(occupied)
        self.assertEqual(self.light, device)

    def testIsOccupied_switchIsOnAndIgnoreMotionSensor_returnsTrue(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.light.turnOn(self.getMockedEventDispatcher())

        (occupied, device) = zone.isOccupied([MotionSensor])
        self.assertTrue(occupied)
        self.assertEqual(self.light, device)

    def testIsOccupied_switchIsOnAndIgnoreLight_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.light.turnOn(self.getMockedEventDispatcher())

        (occupied, device) = zone.isOccupied([Light])
        self.assertFalse(occupied)
        self.assertEqual(None, device)

    def testIsOccupied_switchIsOnAndIgnoreLightAndMotionSensor_returnsFalse(self):
        zone = Zone('ff', [self.light, self.motionSensor])
        self.light.turnOn(self.getMockedEventDispatcher())

        (occupied, device) = zone.isOccupied([Light, MotionSensor])
        self.assertFalse(occupied)
        self.assertEqual(None, device)

    def testIsOccupied_motionEventTriggeredButLightIsOff_returnsTrue(self):
        self.assertFalse(self.light.isOn())

        zone = Zone('ff', [self.light, self.motionSensor, self.illuminanceSensor])
        self.motionSensor._updateLastActivatedTimestamp()
        (occupied, device) = zone.isOccupied()
        self.assertTrue(occupied)
        self.assertEqual(self.motionSensor, device)

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

    def testShareSensorWith_noSharedSensors_returnsFalse(self):
        zone1 = Zone('ff', [self.lightWithIlluminance, self.astroSensor])
        zone2 = Zone('foyer', [])

        self.assertFalse(zone1.shareSensorWith(zone2, Light))

    def testShareSensorWith_sharedSensorsWithNoChannel_returnsFalse(self):
        zone1 = Zone('ff', [self.lightWithIlluminance, self.astroSensor])
        zone2 = Zone('foyer', [self.lightWithIlluminance])

        self.assertFalse(zone1.shareSensorWith(zone2, Light))

    def testShareSensorWith_sharedSensorsWithChannel_returnsTrue(self):
        zone1 = Zone('ff', [self.lightWithIlluminance, self.astroSensor])
        zone2 = Zone('foyer', [self.lightWithIlluminance])

        self.lightWithIlluminance.getChannel = lambda : 'a channel'
        self.assertTrue(zone1.shareSensorWith(zone2, Light))

    def testOnTimerExpired_invalidTimerItem_returnsFalse(self):
        zone = Zone('ff', [self.light])

        isProcessed = zone.onTimerExpired(
                self.getMockedEventDispatcher(), PE.createStringItem('dummy name'))
        self.assertFalse(isProcessed)

    def testOnSwitchedTurnedOn_validItemName_returnsTrue(self):
        zone = Zone('ff', [self.light])

        isProcessed = zone.onSwitchTurnedOn(self.getMockedEventDispatcher(), self.lightItem, None)
        self.assertTrue(isProcessed)

    def testOnSwitchedTurnedOff_validItemName_returnsTrue(self):

        zone = Zone('ff', [self.light])

        isProcessed = zone.onSwitchTurnedOff(self.getMockedEventDispatcher(), self.lightItem, None)
        self.assertTrue(isProcessed)

    def testOnMotionSensorTurnedOn_validItemNameNoIlluminanceSensorNoAstroSensor_returnsFalse(self):
        self.assertFalse(self.light.isOn())

        zone = Zone('ff', [self.light, self.motionSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), MockedZoneManager([zone]), True)
        self.assertFalse(isProcessed)

    def testOnMotionSensorTurnedOn_illuminanceAboveThreshold_returnsFalse(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX + 1))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), MockedZoneManager([zone]), True)
        self.assertFalse(isProcessed)
        self.assertFalse(self.light.isOn())

    def testOnMotionSensorTurnedOn_illuminanceBelowThreshold_turnsOnLight(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), MockedZoneManager([zone]), True)
        self.assertTrue(isProcessed)

        self.assertTrue(self.light.isOn())

    def testOnMotionSensorTurnedOn_notLightOnTime_returnsFalse(self):
        self.astroSensorItem.setState(StringType('MORNING'))

        zone = Zone('ff', [self.light, self.astroSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), None, True)
        self.assertFalse(isProcessed)

    def testOnMotionSensorTurnedOn_notLightOnTimeButIlluminanceBelowThreshold_turnsOnLight(self):
        self.assertFalse(self.light.isOn())
        self.illuminanceSensorItem.setState(DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))
        self.astroSensorItem.setState(StringType('MORNING'))

        zone = Zone('ff', [self.lightWithIlluminance, self.motionSensor,
                self.illuminanceSensor, self.astroSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), MockedZoneManager([zone]), True)
        self.assertTrue(isProcessed)
        self.assertTrue(self.light.isOn())

    def testOnMotionSensorTurnedOn_lightOnTime_turnsOnLight(self):
        self.assertFalse(self.light.isOn())

        self.astroSensorItem.setState(StringType(AstroSensor.LIGHT_ON_TIMES[0]))
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor])
        zone = zone.addAction(TurnOnSwitch())

        isProcessed = zone.dispatchEvent(ZoneEvent.MOTION, self.getMockedEventDispatcher(),
                self.motionSensor.getItem(), MockedZoneManager([zone]), True)
        self.assertTrue(isProcessed)
        self.assertTrue(self.light.isOn())

    def testStr_noParam_returnsNonEmptyString(self):
        zone = Zone('ff', [self.light, self.motionSensor, self.astroSensor, 
                self.illuminanceSensor, self.dimmer, self.fan])
        info = str(zone)

        self.assertTrue(len(info) > 0)

    def testGetNeighborZones_noZoneManager_throwsException(self):
        zone1 = Zone('ff')
        with self.assertRaises(ValueError) as cm:
            zone1.getNeighborZones(None)

        self.assertEqual('zoneManager must not be None', cm.exception.args[0])

    def testGetNeighborZones_noNeighborTypesSpecified_returnsCorrectList(self):
        zone1 = Zone('foyer')
        zone2 = Zone('porch')
        zone3 = Zone('office')

        zone1 = zone1.addNeighbor(Neighbor(zone2.getId(), NeighborType.OPEN_SPACE))
        zone1 = zone1.addNeighbor(Neighbor(zone3.getId(), NeighborType.OPEN_SPACE_MASTER))
        zm = MockedZoneManager([zone1, zone2, zone3])

        self.assertEqual(2, len(zone1.getNeighborZones(zm)))

    def testGetNeighborZones_neighborTypeSpecified_returnsCorrectList(self):
        zone1 = Zone('foyer')
        zone2 = Zone('porch')
        zone3 = Zone('office')

        zone1 = zone1.addNeighbor(Neighbor(zone2.getId(), NeighborType.OPEN_SPACE))
        zone1 = zone1.addNeighbor(Neighbor(zone3.getId(), NeighborType.OPEN_SPACE_MASTER))
        zm = MockedZoneManager([zone1, zone2, zone3])

        zones = zone1.getNeighborZones(zm, [NeighborType.OPEN_SPACE_MASTER])
        self.assertEqual(1, len(zones))
        self.assertEqual(zone3, zones[0])

PE.runUnitTest(ZoneTest)
