import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

#from aaa_modules.layout_model.actions import turn_on_switch
#reload(turn_on_switch)
from aaa_modules.layout_model.actions.turn_on_switch import TurnOnSwitch

from aaa_modules.layout_model.zone import Zone, Level
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Light

from aaa_modules.layout_model.device_test import DeviceTest

ILLUMINANCE_THRESHOLD_IN_LUX = 10
ITEMS = [SwitchItem('TestLightName1'),
      SwitchItem('TestTimerName1'),
      SwitchItem('TestLightName2'),
      SwitchItem('TestTimerName2'),
      NumberItem('IlluminanceSensorName'),
      SwitchItem('TestMotionSensor1'),
      SwitchItem('TestMotionSensor2'),
    ]

# Unit tests for zone_manager.py.
class TurnOnSwitchTest(DeviceTest):

    def setUp(self):
        super(TurnOnSwitchTest, self).setUp()

        [self.lightItem1, self.timerItem1, self.lightItem2, self.timerItem2,
            self.illuminanceSensorItem, self.motionSensorItem1,
            self.motionSensorItem2] = self.getItems()

        self.illuminanceSensor = IlluminanceSensor(self.illuminanceSensorItem)
        self.light1 = Light(self.lightItem1, self.timerItem1,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.light2 = Light(self.lightItem2, self.timerItem2,
                ILLUMINANCE_THRESHOLD_IN_LUX)
        self.motionSensor1 = MotionSensor(self.motionSensorItem1)
        self.motionSensor2 = MotionSensor(self.motionSensorItem2)

        self.zone1 = Zone('foyer', [self.light1, self.illuminanceSensor, self.motionSensor1])
        self.zone2 = Zone('office', [self.light2, self.illuminanceSensor, self.motionSensor2])

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
        self.light1.turnOn(scope.events)
        time.sleep(0.1)

        self.assertTrue(self.turnOn())

    def testOnAction_switchDisablesTriggeringByMotionSensor_returnsFalse(self):
        self.light1 = Light(self.lightItem1, self.timerItem1,
                ILLUMINANCE_THRESHOLD_IN_LUX, True)
        self.zone1 = Zone('foyer', [self.light1, self.illuminanceSensor])

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_switchWasJustTurnedOff_returnsFalse(self):
        self.light1.onSwitchTurnedOff(scope.events, self.light1.getItemName())

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_adjacentZoneWasNotOn_returnsTrue(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE, True) 

        # shared channel
        self.motionSensor1.getChannel = lambda : 'a channel'
        self.motionSensor2.getChannel = lambda : 'a channel'

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertTrue(self.turnOn())

    def testOnAction_adjacentZoneWasJustTurnedOff_returnsFalse(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE, True) 

        # shared channel
        self.motionSensor1.getChannel = lambda : 'a channel'
        self.motionSensor2.getChannel = lambda : 'a channel'

        self.light2.onSwitchTurnedOff(scope.events, self.light2.getItemName())

        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))

        self.assertFalse(self.turnOn())

    def testOnAction_openSpaceMasterNeighborIsOn_returnsFalse(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE_MASTER, True) 

        self.assertFalse(self.turnOn())

    def testOnAction_openSpaceMasterNeighborIsOff_returnsFalse(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE_MASTER, False) 

        self.assertTrue(self.turnOn())

    def testOnAction_openSpaceNeighborIsOn_returnsTrueAndTurnOffNeighbor(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE, True) 
        self.assertTrue(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        time.sleep(0.1)
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceNeighborIsOff_returnsTrue(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE, False) 
        self.assertFalse(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        time.sleep(0.1)
        self.assertTrue(self.zone1.isLightOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceSlaveNeighborIsOn_returnsTrueAndTurnOffNeighbor(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE_SLAVE, True) 
        self.assertTrue(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        time.sleep(0.1)
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_openSpaceSlaveNeighborIsOff_returnsTrue(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE_SLAVE, False) 
        self.assertFalse(self.zone2.isLightOn())

        self.assertTrue(self.turnOn())
        time.sleep(0.1)
        self.assertTrue(self.zone1.isLightOn())
        self.assertFalse(self.zone2.isLightOn())

    def testOnAction_renewTimerWhenBothMasterAndSlaveAreOn_returnsTrueAndNotTurningOffNeighbor(self):
        self.setUpNeighborRelationship(NeighborType.OPEN_SPACE_SLAVE, True) 
        self.lightItem1.setState(scope.OnOffType.ON)

        self.assertTrue(self.turnOn())
        time.sleep(0.1)
        self.assertTrue(self.zone2.isLightOn())

    def turnOn(self):
        class MockZoneManager:
            def __init__(self, zone):
                self.zone = zone

            def getZoneById(self, id):
                return self.zone

        zm = MockZoneManager(self.zone2)
        return TurnOnSwitch().onAction(events, self.zone1, zm)

    # Helper method to set up the relationship between zone1 and zone2.
    def setUpNeighborRelationship(self, type, neighborLightOn):
        self.illuminanceSensorItem.setState(
                DecimalType(ILLUMINANCE_THRESHOLD_IN_LUX - 1))
        self.zone1 = self.zone1.addNeighbor(Neighbor(self.zone2.getId(), type))
        
        if neighborLightOn:
            self.lightItem2.setState(scope.OnOffType.ON)

PE.runUnitTest(TurnOnSwitchTest)
