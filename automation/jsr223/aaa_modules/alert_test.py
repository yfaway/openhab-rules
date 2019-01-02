import unittest
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory

from aaa_modules import alert
reload(alert)
from aaa_modules.alert import *

SUBJECT = "a subject"
BODY = 'a body\n line2'
MODULE = 'a module'
INTERVAL_BETWEEN_ALERTS_IN_MINUTES = 5
EMAIL_ADDRESSES = 'asdf@here.com'

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class AlertTest(unittest.TestCase):
    def testCreateInfoAlert_withSubject_returnsNewObject(self):
        alert = Alert.createInfoAlert(SUBJECT)
        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(None, alert.getBody())
        self.assertEqual(0, len(alert.getAttachmentUrls()))
        self.assertEqual(None, alert.getModule())
        self.assertEqual(None, alert.getEmailAddresses())
        self.assertEqual(-1, alert.getIntervalBetweenAlertsInMinutes())
        self.assertTrue(alert.isInfoLevel())

    def testCreateWarningAlert_withSubject_returnsNewObject(self):
        alert = Alert.createWarningAlert(SUBJECT)
        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(None, alert.getBody())
        self.assertEqual(0, len(alert.getAttachmentUrls()))
        self.assertEqual(None, alert.getModule())
        self.assertEqual(-1, alert.getIntervalBetweenAlertsInMinutes())
        self.assertTrue(alert.isWarningLevel())

    def testCreateCriticalAlert_withSubjectAndBody_returnsNewObject(self):
        alert = Alert.createCriticalAlert(SUBJECT, BODY)
        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(BODY, alert.getBody())
        self.assertEqual(0, len(alert.getAttachmentUrls()))
        self.assertTrue(alert.isCriticalLevel())

    def testFromJson_missingSubject_raiseException(self):
        json = '{' + '"body":"{}","level":"blah"'.format(SUBJECT, BODY) + '}'
        with self.assertRaises(ValueError) as cm:
            alert = Alert.fromJson(json)
        self.assertEqual('Missing subject value.', cm.exception.args[0])

    def testFromJson_withSubject_returnsNewObject(self):
        json = '{"subject":"' + SUBJECT + '"}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(None, alert.getBody())
        self.assertTrue(alert.isInfoLevel())

    def testFromJson_withSubjectAndEmailAddresses_returnsNewObject(self):
        json = '{' + '"subject":"{}","emailAddresses":"{}"'.format(
                SUBJECT, EMAIL_ADDRESSES) + '}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(EMAIL_ADDRESSES, alert.getEmailAddresses())
        self.assertEqual(None, alert.getBody())
        self.assertTrue(alert.isInfoLevel())

    def testFromJson_withSubjectAndBody_returnsNewObject(self):
        json = '{' + '"subject":"{}","body":"{}"'.format(SUBJECT, BODY) + '}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(BODY, alert.getBody())
        self.assertTrue(alert.isInfoLevel())

    def testFromJson_withSubjectBodyAndLevel_returnsNewObject(self):
        json = '{' + '"subject":"{}","body":"{}","level":"warning"'.format(SUBJECT, BODY) + '}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(BODY, alert.getBody())
        self.assertTrue(alert.isWarningLevel())

    def testFromJson_invalidLevel_raiseException(self):
        json = '{' + '"subject":"{}","body":"{}","level":"blah"'.format(SUBJECT, BODY) + '}'
        with self.assertRaises(ValueError) as cm:
            alert = Alert.fromJson(json)

    def testFromJson_withSubjectBodyAndModule_returnsNewObject(self):
        json = '{' + '"subject":"{}","body":"{}","module":"{}","intervalBetweenAlertsInMinutes":{}'.format(
                SUBJECT, BODY, MODULE, INTERVAL_BETWEEN_ALERTS_IN_MINUTES) + '}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(BODY, alert.getBody())
        self.assertEqual(MODULE, alert.getModule())
        self.assertEqual(INTERVAL_BETWEEN_ALERTS_IN_MINUTES, alert.getIntervalBetweenAlertsInMinutes())
        self.assertTrue(alert.isInfoLevel())

    def testFromJson_missingIntervalBetweenAlertsInMinutes_returnsNewObject(self):
        json = '{' + '"subject":"{}","body":"{}","module":"{}"'.format(
                SUBJECT, BODY, MODULE) + '}'
        with self.assertRaises(ValueError) as cm:
            alert = Alert.fromJson(json)
        self.assertEqual('Invalid intervalBetweenAlertsInMinutes value: -1', cm.exception.args[0])

#run_test(AlertTest, logger) 
