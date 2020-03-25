from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import SwitchItem
from org.eclipse.smarthome.core.library.types import DecimalType

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

#from aaa_modules.layout_model.actions import turn_on_switch
#reload(turn_on_switch)
from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.mocked_zone_manager import MockedZoneManager
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.devices.astro_sensor import AstroSensor
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor
from aaa_modules.layout_model.devices.switch import Light

from aaa_modules.layout_model.device_test import DeviceTest

ILLUMINANCE_THRESHOLD_IN_LUX = 10
ITEMS = [SwitchItem('TestLightName1'),
      SwitchItem('TestTimerName1'),
      SwitchItem('TestLightName2'),
      SwitchItem('TestTimerName2'),
      NumberItem('IlluminanceSensorName'),
      SwitchItem('TestMotionSensor1'),
      SwitchItem('TestMotionSensor2'),
      SwitchItem('TestLightName3'),
      SwitchItem('TestTimerName3'),
    ]

# Unit tests for zone_manager.py.
class TurnOnSwitchTest(DeviceTest):

    def setUp(self):
        super(TurnOnSwitchTest, self).setUp()

        [self.lightItem1, self.timerItem1, self.lightItem2, self.timerItem2,
            self.illuminanceSensorItem, self.motionSensorItem1,
            self.motionSensorItem2, self.lightItem3, self.timerItem3] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light1 = Light(self.lightItem1, self.timerItem1,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.light2 = Light(self.lightItem2, self.timerItem2,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.light3 = Light(self.lightItem3, self.timerItem3,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.motionSensor1 = MotionSensor(self.motionSensorItem1)
        self.motionSensor2 = MotionSensor(self.motionSensorItem2)

        self.zone1 = Zone('great room', [self.light1, self.illuminanceSensor, self.motionSensor1])
        self.zone2 = Zone('kitchen', [self.light2, self.illuminanceSensor, self.motionSensor2])
        self.zone3 = Zone('foyer', [self.light3, self.illuminanceSensor])

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)
                elif isinstance(item, SwitchItem):
                    item.setState(UndefState)

        return ITEMS

    def testOnAction_illuminanceBelowThreshold_turnsOnLight(self):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertTrue(self.turnOn())

    def testOnAction_illuminanceAboveThreshold_returnsFalse(self):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX + 1))

        self.assertFalse(self.turnOn())

    def testOnAction_renewTimerIfLightIsAlreadyOnEvenIfIlluminanceIsAboveThreshold_returnsTrue(self):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX + 1))
        self.light1.turnOn(self.getMockedEventDispatcher())

        self.assertTrue(self.turnOn())

    def testOnAction_switchDisablesTriggeringByMotionSensor_returnsFalse(self):
        self.light1 = Light(self.lightItem1, self.timerItem1,
                ILLUMINANCE_THRESHOLD_IN_LUX, True)
        self.zone1 = Zone('foyer', [self.light1, self.illuminanceSensor])

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_switchWasJustTurnedOff_returnsFalse(self):
        self.light1.onSwitchTurnedOff(self.getMockedEventDispatcher(), self.light1.getItemName())

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_adjacentZoneWasNotOn_returnsTrue(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE, True) 

        # shared channel
        self.motionSensor1.getChannel = lambda : 'a channel'
        self.motionSensor2.getChannel = lambda : 'a channel'

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertTrue(self.turnOn())

    def testOnAction_adjacentZoneWasJustTurnedOff_returnsFalse(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE, True) 

        # shared channel
        self.motionSensor1.getChannel = lambda : 'a channel'
        self.motionSensor2.getChannel = lambda : 'a channel'

        self.light2.onSwitchTurnedOff(self.getMockedEventDispatcher(), self.light2.getItemName())

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_openSpaceMasterNeighborIsOn_returnsFalse(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE_MASTER, True) 

        self.assertFalse(self.turnOn())

    def testOnAction_openSpaceMasterNeighborIsOff_returnsFalse(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE_MASTER, False) 

        self.assertTrue(self.turnOn())

    def testOnAction_openSpaceNeighborIsOn_returnsTrueAndTurnOffNeighbor(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE, True) 
        self.assertTrue(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceNeighborIsOff_returnsTrue(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE, False) 
        self.assertFalse(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        self.assertTrue(self.zone1.isLightOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceSlaveNeighborIsOn_returnsTrueAndTurnOffNeighbor(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE_SLAVE, True) 
        self.assertTrue(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceSlaveNeighborIsOff_returnsTrue(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE_SLAVE, False) 
        self.assertFalse(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        self.assertTrue(self.zone1.isLightOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_renewTimerWhenBothMasterAndSlaveAreOn_returnsTrueAndNotTurningOffNeighbor(self):
        self.setUpNeighborRelationship(self.zone2, NeighborType.OPEN_SPACE_SLAVE, True) 
        self.lightItem1.setState(scope.OnOffType.ON)

        self.assertTrue(self.turnOn())
        self.assertTrue(self.zone2.isLightOn())

    def testOnAction_masterIsOn_returnsTrueAndNotTurningOffOpenSpaceNeighbor(self):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        # zone3 (foyer) is an open space neighbor with zone2
        self.zone2 = self.zone2.addNeighbor(Neighbor(self.zone3.getId(), NeighborType.OPEN_SPACE))
        # zone2 (kitchen) is an open space slave with zone1 (great room)
        self.zone2 = self.zone2.addNeighbor(Neighbor(self.zone1.getId(), NeighborType.OPEN_SPACE_MASTER))

        # Turn on the light in the great room and the foyer. 
        # We want to make sure that when the motion sensor in the kitchen is
        # triggered, it won't be turn on, and also the foyer light must not
        # be turned off.
        # The rationale is that someone just open the door to come to the foyer
        # area. However, as the great room light was already on, that indicates
        # someone is already in that area. As such, any movement in that 
        # area must not prematurely turn off the the foyer light.
        self.lightItem1.setState(scope.OnOffType.ON)
        self.lightItem3.setState(scope.OnOffType.ON)

        eventInfo = EventInfo(ZoneEvent.MOTION, ITEMS[0],
                self.zone2, self.createMockedZoneManager(), self.getMockedEventDispatcher())
        returnVal = TurnOnSwitch().onAction(eventInfo)
        self.assertFalse(returnVal)
        self.assertFalse(self.zone2.isLightOn())
        self.assertTrue(self.zone3.isLightOn())

    def turnOn(self):
        eventInfo = EventInfo(ZoneEvent.MOTION, ITEMS[0],
                self.zone1, self.createMockedZoneManager(), self.getMockedEventDispatcher())
        return TurnOnSwitch().onAction(eventInfo)

    # Helper method to set up the relationship between the provided zone and zone1.
    def setUpNeighborRelationship(self, zone, type, neighborLightOn):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))
        self.zone1 = self.zone1.addNeighbor(Neighbor(zone.getId(), type))
        
        if neighborLightOn:
            self.lightItem2.setState(scope.OnOffType.ON)

    def createMockedZoneManager(self):
        return MockedZoneManager([self.zone1, self.zone2, self.zone3])

PE.runUnitTest(TurnOnSwitchTest)
