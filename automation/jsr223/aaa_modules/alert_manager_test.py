import unittest

#from aaa_modules import alert_manager
#reload(alert_manager)

from aaa_modules.alert import *
from aaa_modules.alert_manager import *
from aaa_modules import cast_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

SUBJECT = 'This is a test alert'
MODULE = 'a module'

# Unit tests for alert_manager.
class AlertManagerTest(unittest.TestCase):
    def setUp(self):
        AlertManager._setTestMode(True)
        AlertManager.reset()
        cast_manager._setTestMode(True)

    def tearDown(self):
        cast_manager._setTestMode(False)
        AlertManager._setTestMode(False)

    def testProcessAlert_missingAlert_throwsException(self):
        with self.assertRaises(ValueError) as cm:
            AlertManager.processAlert(None)
        self.assertEqual('Invalid alert.', cm.exception.args[0])

    def testProcessAlert_warningAlert_returnsTrue(self):
        alert = Alert.createWarningAlert(SUBJECT)
        result = AlertManager.processAlert(alert)
        self.assertTrue(result)

        casts = cast_manager.getAllCasts()
        for cast in casts:
            self.assertEqual(SUBJECT, cast.getLastTtsMessage())

        self.assertEqual(alert.getSubject(), AlertManager._lastEmailedSubject)

    def testProcessAlert_audioWarningAlert_returnsTrue(self):
        alert = Alert.createAudioWarningAlert(SUBJECT)
        result = AlertManager.processAlert(alert)
        self.assertTrue(result)

        casts = cast_manager.getAllCasts()
        for cast in casts:
            self.assertEqual(SUBJECT, cast.getLastTtsMessage())

        self.assertEqual(None, AlertManager._lastEmailedSubject)

    def testProcessAlert_criticalAlert_returnsTrue(self):
        alert = Alert.createCriticalAlert(SUBJECT)
        result = AlertManager.processAlert(alert)
        self.assertTrue(result)

        casts = cast_manager.getAllCasts()
        for cast in casts:
            self.assertEqual(SUBJECT, cast.getLastTtsMessage())

    def testProcessAlert_withinInterval_returnsFalse(self):
        alert = Alert.createCriticalAlert(SUBJECT, None, [], MODULE, 1)
        self.assertTrue(AlertManager.processAlert(alert))

        # send alert would be ignored dued to interval threshold
        self.assertFalse(AlertManager.processAlert(alert))

        # but another alert with module would go through
        self.assertTrue(AlertManager.processAlert(Alert.createCriticalAlert(SUBJECT)))

    def testProcessAdminAlert_warningAlert_returnsTrue(self):
        alert = Alert.createWarningAlert(SUBJECT)
        result = AlertManager.processAdminAlert(alert)
        self.assertTrue(result)
        self.assertEqual(alert.getSubject(), AlertManager._lastEmailedSubject)

    def testGetEmailAddresses_noParams_returnsNonEmptyList(self):
        emails = AlertManager._getOwnerEmailAddresses()
        self.assertTrue(len(emails) > 0)

PE.runUnitTest(AlertManagerTest)
