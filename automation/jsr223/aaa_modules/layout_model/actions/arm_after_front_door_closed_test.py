import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.immutable_zone_manager import ImmutableZoneManager
from aaa_modules.layout_model.alarm_partition import AlarmPartition
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.device_test import DeviceTest
from aaa_modules.layout_model.devices.contact import Door

#from aaa_modules.layout_model.actions import arm_after_front_door_closed
#reload(arm_after_front_door_closed)
from aaa_modules.layout_model.actions.arm_after_front_door_closed import ArmAfterFrontDoorClosed

ITEMS = [SwitchItem('Door1'), SwitchItem('Door2'),
    SwitchItem('AlarmStatus'), NumberItem('_AlarmMode'),
    SwitchItem('ExternalMotionSensor'), SwitchItem('InternalMotionSensor')]

class MockZoneManager:
    def __init__(self, alarmPartition, zones):
        self.alarmPartition = alarmPartition
        self.zones = list(zones)

    def getDevicesByType(self, cls):
        return [self.alarmPartition]

    def getZones(self):
        return self.zones

# Unit tests for arm_after_front_door_closed.py.
class ArmAfterFrontDoorClosedTest(DeviceTest):
    def setUp(self):
        super(ArmAfterFrontDoorClosedTest, self).setUp()

        self.alarmPartition = AlarmPartition(ITEMS[2], ITEMS[3])
        self.externalMotionSensor = MotionSensor(ITEMS[4])
        self.internalMotionSensor = MotionSensor(ITEMS[5])

        self.zone1 = Zone.createExternalZone('porch') \
            .addDevice(Door(ITEMS[0])) \
            .addDevice(self.externalMotionSensor)

        self.zone2 = Zone('foyer', [self.internalMotionSensor, self.alarmPartition])

        self.mockZoneManager= MockZoneManager(self.alarmPartition,
                [self.zone1, self.zone2])

        AlertManager._setTestMode(True)
        AlertManager.reset()

    def tearDown(self):
        AlertManager._setTestMode(False)
        super(ArmAfterFrontDoorClosedTest, self).tearDown()

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)

        return ITEMS

    def testOnAction_motionTriggeredInAnExternalZone_ignoreMotionEventAndContinueToArm(self):
        ITEMS[0].setState(scope.OnOffType.OFF) # close door
        self.alarmPartition.disarm(self.getMockedEventDispatcher())

        eventInfo = EventInfo(ZoneEvent.CONTACT_CLOSED, ITEMS[0],
                self.zone1, self.mockZoneManager, self.getMockedEventDispatcher())
        value = ArmAfterFrontDoorClosed(0.1).onAction(eventInfo)
        self.assertTrue(value)

        time.sleep(0.1)
        # simulate a motion event
        self.externalMotionSensor._updateLastActivatedTimestamp()

        time.sleep(0.2)
        self.assertTrue(self.alarmPartition.isArmedAway())

    def testOnAction_doorClosedWithNoPresenceEvent_armAndReturnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.OFF) # close door
        self.alarmPartition.disarm(self.getMockedEventDispatcher())

        eventInfo = EventInfo(ZoneEvent.CONTACT_CLOSED, ITEMS[0],
                self.zone1, self.mockZoneManager, self.getMockedEventDispatcher())

        value = ArmAfterFrontDoorClosed(0.1).onAction(eventInfo)
        self.assertTrue(value)

        time.sleep(0.2)
        self.assertTrue(self.alarmPartition.isArmedAway())

    def testOnAction_doorClosedWithPresenceEvent_notArmedAndReturnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.OFF) # close door
        self.alarmPartition.disarm(self.getMockedEventDispatcher())

        eventInfo = EventInfo(ZoneEvent.CONTACT_CLOSED, ITEMS[0],
                self.zone1, self.mockZoneManager, self.getMockedEventDispatcher())
        value = ArmAfterFrontDoorClosed(0.1).onAction(eventInfo)
        self.assertTrue(value)

        time.sleep(0.1)
        # simulate a motion event
        self.internalMotionSensor._updateLastActivatedTimestamp()

        time.sleep(0.1)
        self.assertFalse(self.alarmPartition.isArmedAway())

PE.runUnitTest(ArmAfterFrontDoorClosedTest)
