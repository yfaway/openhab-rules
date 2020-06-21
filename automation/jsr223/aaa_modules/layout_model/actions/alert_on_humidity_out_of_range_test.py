import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.types import DecimalType

from aaa_modules import cast_manager
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model.actions import alert_on_humidity_out_of_range
#reload(alert_on_humidity_out_of_range)
from aaa_modules.layout_model.actions.alert_on_humidity_out_of_range import AlertOnHumidityOutOfRange

ITEMS = [NumberItem('humidity_sensor')]

# Unit tests for alert_on_humidity_out_of_range.py.
class AlertOnHumidityOutOfRangeTest(DeviceTest):
    def setUp(self):
        self.action = AlertOnHumidityOutOfRange(35, 50, 3)
        self.zone1 = Zone('great room').addDevice(HumiditySensor(ITEMS[0]))

        AlertManager._setTestMode(True)
        AlertManager.reset()
        cast_manager._setTestMode(True)

    def tearDown(self):
        cast_manager._setTestMode(False)
        AlertManager._setTestMode(False)

    def getItems(self, resetState = False):
        return ITEMS

    def testOnAction_zoneDoesNotContainSensor_returnsFalse(self):
        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], Zone('innerZone'),
                None, self.getMockedEventDispatcher())
        value = AlertOnHumidityOutOfRange().onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_zoneIsExternal_returnsFalse(self):
        zone = Zone.createExternalZone('porch').addDevice(HumiditySensor(ITEMS[0]))
        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], zone,
                None, self.getMockedEventDispatcher())
        value = AlertOnHumidityOutOfRange().onAction(eventInfo)
        self.assertFalse(value)

    def testOnAction_humidityJustBelowMinThresholdButAboveNoticeThreshold_sendsNoAlert(self):
        ITEMS[0].setState(DecimalType(34))
        self.sendEventAndAssertNoAlert()

    def testOnAction_lowHumidityAtFirstThreshold_TrueAndSendAlert(self):
        ITEMS[0].setState(DecimalType(32))
        self.sendEventAndAssertAlertContainMessage('below the threshold')

    def testOnAction_lowHumidityButNotYetAtSecondThreshold_doNotSendAlert(self):
        ITEMS[0].setState(DecimalType(32))
        self.sendEventAndAssertAlertContainMessage('below the threshold')

        ITEMS[0].setState(DecimalType(33))
        self.sendEventAndAssertNoAlert()

    def testOnAction_lowHumidityAtSecondThreshold_sendAlert(self):
        ITEMS[0].setState(DecimalType(32))
        self.sendEventAndAssertAlertContainMessage('below the threshold')

        ITEMS[0].setState(DecimalType(29))
        self.sendEventAndAssertAlertContainMessage('below the threshold')

    def testOnAction_humidityJustAboveMinThresholdButAboveNoticeThreshold_sendsNoAlert(self):
        ITEMS[0].setState(DecimalType(51))
        self.sendEventAndAssertNoAlert()

    def testOnAction_highHumidityAtFirstThreshold_TrueAndSendAlert(self):
        ITEMS[0].setState(DecimalType(53))
        self.sendEventAndAssertAlertContainMessage('above the threshold')

    def testOnAction_highHumidityButNotYetAtSecondThreshold_doNotSendAlert(self):
        ITEMS[0].setState(DecimalType(53))
        self.sendEventAndAssertAlertContainMessage('above the threshold')

        ITEMS[0].setState(DecimalType(54))
        self.sendEventAndAssertNoAlert()

    def testOnAction_highHumidityAtSecondThreshold_sendAlert(self):
        ITEMS[0].setState(DecimalType(54))
        self.sendEventAndAssertAlertContainMessage('above the threshold')

        ITEMS[0].setState(DecimalType(56))
        self.sendEventAndAssertAlertContainMessage('above the threshold')

    def testOnAction_humidityWithinThreshold_returnsTrueAndSendsNoAlert(self):
        ITEMS[0].setState(DecimalType(40))
        self.sendEventAndAssertNoAlert()

    def testOnAction_humidityBackToNormal_returnsTrueAndSendsInfoAlert(self):
        # initially below threshold
        ITEMS[0].setState(DecimalType(20))
        self.sendEventAndAssertAlertContainMessage('below the threshold')

        # now back to normal
        ITEMS[0].setState(DecimalType(40))
        self.sendEventAndAssertAlertContainMessage('back to the normal range')

    def sendEventAndAssertNoAlert(self):
        AlertManager.reset()

        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertEqual(None, AlertManager._lastEmailedSubject)

    def sendEventAndAssertAlertContainMessage(self, message):
        AlertManager.reset()

        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = self.action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertTrue(message in AlertManager._lastEmailedSubject)

PE.runUnitTest(AlertOnHumidityOutOfRangeTest)
