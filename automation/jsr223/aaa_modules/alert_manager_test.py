import unittest

from org.slf4j import Logger, LoggerFactory
from openhab.testing import run_test

from aaa_modules import alert
reload(alert)
from aaa_modules.alert import *

from aaa_modules import alert_manager
reload(alert_manager)
from aaa_modules import alert_manager

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

SUBJECT = 'This is a test alert'

# Unit tests for alert_manager.
class AlertManagerTest(unittest.TestCase):
    def setUp(self):
        cast_manager._setTestMode(True)

    def tearDown(self):
        cast_manager._setTestMode(False)

    def testProcessAlert_missingAlert_throwsException(self):
        with self.assertRaises(ValueError) as cm:
            alert_manager.processAlert(None)
        self.assertEqual('Invalid alert.', cm.exception.args[0])

    def testProcessAlert_warningAlert_returnsTrue(self):
        alert = Alert.createWarningAlert('This is a test alert')
        alert_manager.processAlert(alert)

        casts = cast_manager.getAllCasts()
        for cast in casts:
            self.assertEqual(SUBJECT, cast.getLastTtsMessage())

    def testProcessAlert_criticalAlert_returnsTrue(self):
        alert = Alert.createCriticalAlert('This is a test alert')
        alert_manager.processAlert(alert)

        casts = cast_manager.getAllCasts()
        for cast in casts:
            self.assertEqual(SUBJECT, cast.getLastTtsMessage())

run_test(AlertManagerTest, logger) 
