from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

#from aaa_modules.layout_model.actions import turn_off_adjacent_zones
#reload(turn_off_adjacent_zones)
from aaa_modules.layout_model.actions.turn_off_adjacent_zones import TurnOffAdjacentZones

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.mocked_zone_manager import MockedZoneManager
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.devices.switch import Fan, Light

from aaa_modules.layout_model.device_test import DeviceTest

ILLUMINANCE_THRESHOLD_IN_LUX = 10
ITEMS = [SwitchItem('TestLightName1'),
      SwitchItem('TestLightName2'),
      SwitchItem('TestLightName3'),
      SwitchItem('TestFanName'),
    ]

# Unit tests for turn_off_adjacent_zones.py
class TurnOffAdjacentZonesTest(DeviceTest):

    def setUp(self):
        super(TurnOffAdjacentZonesTest, self).setUp()

        [self.lightItem1, self.lightItem2, self.lightItem3, self.fanItem] = self.getItems()

        self.light1 = Light(self.lightItem1, 5)
        self.light2 = Light(self.lightItem2, 5)
        self.light3 = Light(self.lightItem3, 5,
                ILLUMINANCE_THRESHOLD_IN_LUX, False, "0-23:59") # always stay on
        self.fan = Fan(self.fanItem, 5)

        self.washroom = Zone('washroom', [self.light1])
        self.shower = Zone('shower', [self.fan])
        self.lobby = Zone('lobby', [self.light2])
        self.foyer = Zone('foyer', [self.light3])
        self.zoneManager = MockedZoneManager(
                [self.washroom, self.shower, self.lobby, self.foyer])

        self.lobby = self.lobby.addNeighbor(
                Neighbor(self.foyer.getId(), NeighborType.OPEN_SPACE))

        self.washroom = self.washroom.addNeighbor(
                Neighbor(self.lobby.getId(), NeighborType.OPEN_SPACE))
        self.washroom = self.washroom.addNeighbor(
                Neighbor(self.shower.getId(), NeighborType.OPEN_SPACE))

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)

        return ITEMS

    def testOnAction_normalOpenSpaceNeighbor_turnsOffLight(self):
        self.lightItem2.setState(scope.OnOffType.ON)

        self.assertTrue(self.turnOff(self.washroom))
        self.assertFalse(self.lobby.isLightOn())

    def testOnAction_openSpaceButDisableTurnOffByNeightbor_mustNotTurnsOffLight(self):
        self.lightItem3.setState(scope.OnOffType.ON)

        self.assertTrue(self.turnOff(self.lobby))
        self.assertTrue(self.foyer.isLightOn())

    def testOnAction_fanZone_returnsFalse(self):
        self.fanItem.setState(scope.OnOffType.ON)
        self.assertFalse(self.turnOff(self.shower))

    def testOnAction_neighborWithFan_mustNotTurnOffNeighborFan(self):
        self.fanItem.setState(scope.OnOffType.ON)
        self.lightItem2.setState(scope.OnOffType.ON)

        self.assertTrue(self.turnOff(self.washroom))
        self.assertFalse(self.lobby.isLightOn())
        self.assertEqual(scope.OnOffType.ON, self.fanItem.getState())

    def turnOff(self, zone):
        eventInfo = EventInfo(ZoneEvent.SWITCH_TURNED_ON, ITEMS[0], zone,
                self.zoneManager, self.getMockedEventDispatcher())

        return TurnOffAdjacentZones().onAction(eventInfo)

PE.runUnitTest(TurnOffAdjacentZonesTest)
