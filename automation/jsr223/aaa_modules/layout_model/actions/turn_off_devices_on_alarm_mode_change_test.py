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
from aaa_modules.layout_model.devices.switch import Light
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
#from aaa_modules.layout_model.actions import turn_off_devices_on_alarm_mode_change
#reload(turn_off_devices_on_alarm_mode_change)
from aaa_modules.layout_model.actions.turn_off_devices_on_alarm_mode_change import TurnOffDevicesOnAlarmModeChange

ITEMS = [SwitchItem('_testMotion'),
         SwitchItem('_testAlarmStatus'),
         NumberItem('_testArmMode'),
         SwitchItem('_testLight'),
         SwitchItem('_testTimer') ]

# Unit tests for turn-off-devices-on-alarm-mode-change.py.
class TurnOffDevicesOnAlarmModeChangeTest(DeviceTest):
    def setUp(self):
        super(TurnOffDevicesOnAlarmModeChangeTest, self).setUp()

        self.audioSink = ChromeCastAudioSink('prefix', 'sinkName')
        self.partition = AlarmPartition(ITEMS[1], ITEMS[2])
        self.light = Light(ITEMS[3], ITEMS[4])

        self.action = TurnOffDevicesOnAlarmModeChange()

        self.audioSink._setTestMode()

        self.audioSink.playStream("http://stream")
        self.light.turnOn(self.getMockedEventDispatcher())
        self.partition.disarm(self.getMockedEventDispatcher())

    def getItems(self, resetState = False):
        return ITEMS

    def testOnAction_armedAwayEvent_turnOffDevicesAndReturnsTrue(self):
        (zone, zm, eventInfo) = self.createTestData(ZoneEvent.PARTITION_ARMED_AWAY)
        self.assertTrue(zone.isLightOn())

        self.invokeActionAndassertDevicesTurnedOff(zone, eventInfo)

    def testOnAction_disarmEvent_turnOffDevicesAndReturnsTrue(self):
        (zone, zm, eventInfo) = self.createTestData(ZoneEvent.PARTITION_DISARMED_FROM_AWAY)
        self.assertTrue(zone.isLightOn())

        self.invokeActionAndassertDevicesTurnedOff(zone, eventInfo)

    def invokeActionAndassertDevicesTurnedOff(self, zone, eventInfo):
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)

        self.assertFalse(zone.isLightOn())
        self.assertEqual("pause", self.audioSink._getLastTestCommand())

    def createTestData(self, zoneEvent):
        '''
        :return: a list of two zones, the mocked zone manager, and the event dispatcher
        :rtype: list
        '''

        self.partition.armAway(self.getMockedEventDispatcher())

        zone = Zone('porch', [self.partition, self.light, self.audioSink])
        zm = MockedZoneManager([zone])
        eventInfo = EventInfo(zoneEvent, ITEMS[0],
                zone, zm, self.getMockedEventDispatcher())

        return [zone, zm, eventInfo]

PE.runUnitTest(TurnOffDevicesOnAlarmModeChangeTest)
