import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem

from aaa_modules import cast_manager
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.event_info import EventInfo
from aaa_modules.layout_model.zone import Zone, Level, ZoneEvent
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.layout_model.device_test import DeviceTest

from aaa_modules.layout_model.actions import alert_on_humidity_out_of_range
reload(alert_on_humidity_out_of_range)
from aaa_modules.layout_model.actions.alert_on_humidity_out_of_range import AlertOnHumidityOutOfRange

ITEMS = [NumberItem('humidity_sensor')]

# Unit tests for alert_on_humidity_out_of_range.py.
class AlertOnHumidityOutOfRangeTest(DeviceTest):
    def setUp(self):
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

    def testOnAction_humidityBelowThreshold_TrueAndSendAlert(self):
        ITEMS[0].setState(DecimalType(20))

        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = AlertOnHumidityOutOfRange().onAction(eventInfo)
        self.assertTrue(value)

        self.assertTrue("below the threshold" in AlertManager._lastEmailedSubject)

    def testOnAction_humidityAboveThreshold_returnsTrueAndSendAlert(self):
        ITEMS[0].setState(DecimalType(60))

        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = AlertOnHumidityOutOfRange().onAction(eventInfo)
        self.assertTrue(value)

        self.assertTrue("above the threshold" in AlertManager._lastEmailedSubject)

    def testOnAction_humidityWithinThreshold_returnsTrueAndSendsNoAlert(self):
        ITEMS[0].setState(DecimalType(40))

        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = AlertOnHumidityOutOfRange().onAction(eventInfo)
        self.assertTrue(value)

        self.assertEqual(None, AlertManager._lastEmailedSubject)

    def testOnAction_humidityBackToNormal_returnsTrueAndSendsInfoAlert(self):
        ITEMS[0].setState(DecimalType(20))

        action = AlertOnHumidityOutOfRange()
        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())

        # initially below threshold
        value = action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertTrue('below the threshold' in AlertManager._lastEmailedSubject)

        # now back to normal
        ITEMS[0].setState(DecimalType(40))
        eventInfo = EventInfo(ZoneEvent.HUMIDITY_CHANGED, ITEMS[0], self.zone1,
                None, self.getMockedEventDispatcher())
        value = action.onAction(eventInfo)
        self.assertTrue(value)
        self.assertTrue('back to the normal range' in AlertManager._lastEmailedSubject)

PE.runUnitTest(AlertOnHumidityOutOfRangeTest)
