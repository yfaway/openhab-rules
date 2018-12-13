import unittest
from openhab.testing import run_test
from org.slf4j import Logger, LoggerFactory

from aaa_modules import alert
reload(alert)
from aaa_modules.alert import *

SUBJECT = "a subject"
BODY = 'a body'

LOGGER = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class AlertTest(unittest.TestCase):
    def testCreateSimpleAlert_withSubject_returnsNewObject(self):
        alert = Alert.createSimpleAlert(Level.INFO, SUBJECT)
        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(None, alert.getBody())
        self.assertTrue(alert.isInfoLevel())

    def testCreateSimpleAlert_withSubjectAndBody_returnsNewObject(self):
        alert = Alert.createSimpleAlert(Level.CRITICAL, SUBJECT, BODY)
        self.assertEqual(SUBJECT, alert.getSubject())
        self.assertEqual(BODY, alert.getBody())
        self.assertTrue(alert.isCriticalLevel())

    def testFromJson_withSubject_returnsNewObject(self):
        json = '{"subject":"' + SUBJECT + '"}'
        alert = Alert.fromJson(json)

        self.assertEqual(SUBJECT, alert.getSubject())
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

run_test(AlertTest, LOGGER) 

