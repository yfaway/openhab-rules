import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.device_test import DeviceTest
from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.mocked_zone_manager import MockedZoneManager
from aaa_modules.layout_model.zone import Zone, ZoneEvent, Level
from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition
from aaa_modules.layout_model.devices.activity_times import ActivityTimes
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
#from aaa_modules.layout_model.actions import simulate_daytime_presence
#reload(simulate_daytime_presence)
from aaa_modules.layout_model.actions.simulate_daytime_presence import SimulateDaytimePresence

ITEMS = [SwitchItem('_testMotion'),
         SwitchItem('_testAlarmStatus'),
         NumberItem('_testArmMode')]

# Unit tests for simulate_daytime_presence.py.
class SimulateDaytimePresenceTest(DeviceTest):
    def setUp(self):
        super(SimulateDaytimePresenceTest, self).setUp()

        self.partition = AlarmPartition(ITEMS[1], ITEMS[2])
        self.audioSink = ChromeCastAudioSink('prefix', 'sinkName')

        self.action = SimulateDaytimePresence("anUrl", 70, 0.1)

        self.partition.disarm(self.getMockedEventDispatcher())
        self.audioSink._setTestMode()

    def tearDown(self):
        super(SimulateDaytimePresenceTest, self).tearDown()

    def getItems(self, resetState = False):
        return ITEMS

    def testOnAction_wrongEventType_returnsFalse(self):
        (porch, greatRoom, zm, _) = self.createTestData()
        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0],
                porch, zm, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_motionEventOnInternalZone_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.MOTION, ITEMS[0], Zone('porch'),
                None, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_noAlarmPartition_returnsFalse(self):
        (porch, greatRoom, zm, eventInfo) = self.createTestData([self.partition])

        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_noAudioSink_returnsFalse(self):
        (porch, greatRoom, zm, eventInfo) = self.createTestData([self.audioSink])

        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_notInArmAwayMode_returnsFalse(self):
        (porch, greatRoom, zm, eventInfo) = self.createTestData()
        self.partition.disarm(self.getMockedEventDispatcher())

        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_sleepTime_returnsFalse(self):
        timeMap = { 'sleep': '0:00 - 23:59' }
        (porch, greatRoom, zm, eventInfo) = self.createTestData(
                [], [ActivityTimes(timeMap)])

        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_allConditionSatisfied_playsMusicAndReturnsTrue(self):
        (porch, greatRoom, zm, eventInfo) = self.createTestData()

        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual("playStream", self.audioSink._getLastTestCommand())

        time.sleep(0.15)
        self.assertEqual("pause", self.audioSink._getLastTestCommand())

    def testOnAction_multipleTriggering_renewPauseTimerAndReturnsTrue(self):
        (porch, greatRoom, zm, eventInfo) = self.createTestData()

        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual("playStream", self.audioSink._getLastTestCommand())

        time.sleep(0.15)
        self.assertEqual("pause", self.audioSink._getLastTestCommand())

        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual("playStream", self.audioSink._getLastTestCommand())

    def createTestData(self, excludedDevices = [], extraIncludedDevices = []):
        '''
        :return: a list of two zones, the mocked zone manager, and the event dispatcher
        :rtype: list
        '''

        self.partition.armAway(self.getMockedEventDispatcher())

        porch = Zone.createExternalZone('porch').addDevice(self.partition)
        greatRoom = Zone("GR", [self.audioSink], Level.FIRST_FLOOR)

        for d in excludedDevices:
            if porch.hasDevice(d):
                porch = porch.removeDevice(d)

            if greatRoom.hasDevice(d):
                greatRoom = greatRoom.removeDevice(d)

        for d in extraIncludedDevices:
            greatRoom = greatRoom.addDevice(d)

        zm = MockedZoneManager([porch, greatRoom])

        eventInfo = EventInfo(ZoneEvent.MOTION, ITEMS[0],
                porch, zm, self.getMockedEventDispatcher())

        return [porch, greatRoom, zm, eventInfo]

PE.runUnitTest(SimulateDaytimePresenceTest)
