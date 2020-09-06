import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules import cast_manager
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.devices.gas_sensor import SmokeSensor
from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model.actions import alert_on_high_gas_level
#reload(alert_on_high_gas_level)
from aaa_modules.layout_model.actions.alert_on_high_gas_level import AlertOnHighGasLevel

ITEMS = [SwitchItem('gas_state'), NumberItem('gas_value'), ]

# Unit tests for alert_on_high_gas_level.py.
class AlertOnHighGasLevelTest(DeviceTest):
    def setUp(self):
        self.action = AlertOnHighGasLevel()
        self.zone1 = Zone('great room', [], Level.FIRST_FLOOR).addDevice(
                SmokeSensor(ITEMS[1], ITEMS[0])) # index reverse order intentionally

        ITEMS[0].setState(scope.OnOffType.OFF)

        AlertManager._setTestMode(True)
        AlertManager.reset()
        cast_manager._setTestMode(True)

    def tearDown(self):
        cast_manager._setTestMode(False)
        AlertManager._setTestMode(False)

    def getItems(self, resetState = False):
        return ITEMS

    def testOnAction_zoneDoesNotContainSensor_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.GAS_TRIGGER_STATE_CHANGED, ITEMS[0], Zone('innerZone'),
                None, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_crossThreshold_returnsTrueAndSendAlert(self):
        ITEMS[0].setState(scope.OnOffType.ON)
        self.sendEventAndAssertAlertContainMessage('above normal level')

    def testOnAction_noLongerTriggered_returnsTrueAndSendsInfoAlert(self):
        # initially below threshold
        ITEMS[0].setState(scope.OnOffType.ON)
        self.sendEventAndAssertAlertContainMessage('above normal level')

        # now back to normal
        ITEMS[0].setState(scope.OnOffType.OFF)
        self.sendEventAndAssertAlertContainMessage('back to normal')

    def sendEventAndAssertAlertContainMessage(self, message):
        AlertManager.reset()

        eventInfo = EventInfo(ZoneEvent.GAS_TRIGGER_STATE_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertTrue(message in AlertManager._lastEmailedSubject)

PE.runUnitTest(AlertOnHighGasLevelTest)
