import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.devices.contact import Door
from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model.actions import alert_on_door_left_open
#reload(alert_on_door_left_open)
from aaa_modules.layout_model.actions.alert_on_door_left_open import AlertOnExternalDoorLeftOpen

ITEMS = [SwitchItem('Door1'), SwitchItem('Door2')]

# Unit tests for alert_on_door_left_open.py.
class AlertOnExternalDoorLeftOpenTest(DeviceTest):
    def setUp(self):
        self.zone1 = Zone.createExternalZone('porch').addDevice(Door(ITEMS[0]))
        self.zone2 = Zone.createExternalZone('garage').addDevice(Door(ITEMS[1]))

        AlertManager._setTestMode(True)
        AlertManager.reset()

    def tearDown(self):
        AlertManager._setTestMode(False)

    def getItems(self, resetState = False):
        if resetState:
            for item in ITEMS:
                if isinstance(item, SwitchItem):
                    item.setState(scope.OnOffType.OFF)
                elif isinstance(item, SwitchItem):
                    item.setState(UndefState)

        return ITEMS

    def testOnAction_notAnExternalZone_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0], Zone('innerZone'),
                None, self.getMockedEventDispatcher())
        value = AlertOnExternalDoorLeftOpen().onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_externalZoneWithNoDoor_returnsFalseAndTimerStarted(self):
        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0],
                Zone.createExternalZone('aZone'), None, self.getMockedEventDispatcher())
        value = AlertOnExternalDoorLeftOpen().onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_aDoorIsOpen_returnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.ON)

        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0],
                self.zone1, None, self.getMockedEventDispatcher())
        action = AlertOnExternalDoorLeftOpen(0.1)
        value = action.onAction(eventInfo)

        self.assertTrue(value)
        self.assertTrue(action.hasRunningTimer())

        time.sleep(0.3) # wait for the production code timer
        self.assertTrue("door" in AlertManager._lastEmailedSubject)

    def testOnAction_aDoorWasOpenButClosedSoonAfter_returnsTrueAndTimerCancelled(self):
        ITEMS[0].setState(scope.OnOffType.ON)

        eventInfo = EventInfo(ZoneEvent.CONTACT_OPEN, ITEMS[0],
                self.zone1, None, self.getMockedEventDispatcher())

        action = AlertOnExternalDoorLeftOpen()
        value = action.onAction(eventInfo)

        self.assertTrue(value)
        self.assertTrue(action.hasRunningTimer())

        # simulate door closed
        ITEMS[0].setState(scope.OnOffType.OFF)
        value = action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertFalse(action.hasRunningTimer())

PE.runUnitTest(AlertOnExternalDoorLeftOpenTest)
