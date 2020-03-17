from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.device_test import DeviceTest
from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.mocked_zone_manager import MockedZoneManager
from aaa_modules.layout_model.zone import Zone, ZoneEvent
from aaa_modules.layout_model.switch import Fan
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
#from aaa_modules.layout_model.actions import play_music_during_shower
#reload(play_music_during_shower)
from aaa_modules.layout_model.actions.play_music_during_shower import PlayMusicDuringShower

ITEMS = [SwitchItem('Fan1')]

# Unit tests for play_music_during_shower.py.
class PlayMusicDuringShowerTest(DeviceTest):
    def setUp(self):
        self.sink = ChromeCastAudioSink('prefix', 'sinkName')
        self.action = PlayMusicDuringShower("anUrl")

        self.sink._setTestMode()

    def tearDown(self):
        pass

    def getItems(self, resetState = False):
        return ITEMS

    def testOnAction_wrongEventType_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0], Zone('innerZone'),
                None, events)
        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_noAudioSink_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON, ITEMS[0], Zone('innerZone'),
                MockedZoneManager([]), events)
        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_switchOnEventAndAudioSinkInZone_playsStreamAndReturnsTrue(self):
        zone1 = Zone('shower').addDevice(self.sink)

        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON, ITEMS[0], zone1,
                None, events)
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual('playStream', self.sink._getLastTestCommand())

    def testOnAction_switchOnEventAndAudioSinkInNeighborZone_playsStreamAndReturnsTrue(self):
        zone1 = Zone('shower')
        zone2 = Zone('washroom').addDevice(self.sink)

        zone1 = zone1.addNeighbor(Neighbor(zone2.getId(), NeighborType.OPEN_SPACE))

        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON, ITEMS[0], zone1,
                MockedZoneManager([zone1, zone2]), events)
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual('playStream', self.sink._getLastTestCommand())

    def testOnAction_switchOffEvent_pauseStreamAndReturnsTrue(self):
        zone1 = Zone('shower').addDevice(self.sink)

        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_OFF, ITEMS[0], zone1,
                None, events)
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual('pause', self.sink._getLastTestCommand())

PE.runUnitTest(PlayMusicDuringShowerTest)
