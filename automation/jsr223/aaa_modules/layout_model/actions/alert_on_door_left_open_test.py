import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.zone import Zone, Level
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
        value = AlertOnExternalDoorLeftOpen().onAction(
                events, Zone('innerZone'), None)
        self.assertFalse(value)

    def testOnAction_externalZoneWithNoDoor_returnsFalseAndTimerStarted(self):
        value = AlertOnExternalDoorLeftOpen().onAction(
                events, Zone.createExternalZone('aZone'), None)
        self.assertFalse(value)

    def testOnAction_aDoorIsOpen_returnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.ON)

        action = AlertOnExternalDoorLeftOpen(1)
        value = action.onAction(events, self.zone1, None)

        self.assertTrue(value)
        self.assertTrue(action.hasRunningTimer())

        time.sleep(2)
        self.assertTrue("door" in AlertManager._lastEmailedSubject)

    def testOnAction_aDoorWasOpenButClosedSoonAfter_returnsTrueAndTimerCancelled(self):
        ITEMS[0].setState(scope.OnOffType.ON)

        action = AlertOnExternalDoorLeftOpen()
        value = action.onAction(events, self.zone1, None)

        self.assertTrue(value)
        self.assertTrue(action.hasRunningTimer())

        # simulate door closed
        ITEMS[0].setState(scope.OnOffType.OFF)
        value = action.onAction(events, self.zone1, None)
        self.assertTrue(value)
        self.assertFalse(action.hasRunningTimer())

PE.runUnitTest(AlertOnExternalDoorLeftOpenTest)
