import unittest

from org.slf4j import Logger, LoggerFactory
from openhab.jsr223 import scope
from org.eclipse.smarthome.core.library.items import StringItem
from org.eclipse.smarthome.core.library.types import StringType
from openhab.testing import run_test

from aaa_modules.alert_manager import *
import alert_sender

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for alert_sender.py.
class AlertRuleTest(unittest.TestCase):
    _TEST_ITEM_NAME = 'TestAlertItem'

    _oldItemName = None

    def setUp(self):
        AlertManager._setTestMode(True)
        AlertManager.reset()

        if not AlertRuleTest._TEST_ITEM_NAME in scope.items:
            testItem = StringItem(AlertRuleTest._TEST_ITEM_NAME)
            scope.itemRegistry.add(testItem)

        _oldItemName = alert_sender._ALERT_ITEM_NAME
        alert_sender._ALERT_ITEM_NAME = AlertRuleTest._TEST_ITEM_NAME

    def tearDown(self):
        scope.itemRegistry.remove(AlertRuleTest._TEST_ITEM_NAME, True)
        alert_sender._ALERT_ITEM_NAME = AlertRuleTest._oldItemName
        AlertManager._setTestMode(False)

    def testSendAlert(self):
        subject = 'hello'
        msg1 = "{"
        msg1 += "\"subject\":\"{}\"".format(subject)
        msg1 += ",\"body\":\"body msg\""
        msg1 += ",\"module\":\"test\""
        msg1 += ",\"intervalBetweenAlertsInMinutes\":\"2\""
        msg1 += "}"

        item = scope.itemRegistry.get(AlertRuleTest._TEST_ITEM_NAME)
        item.setState(StringType(msg1))
        
        self.assertTrue(alert_sender.sendAlert(None))
        self.assertEqual(subject, AlertManager._lastEmailedSubject)

#run_test(AlertRuleTest, logger) 
