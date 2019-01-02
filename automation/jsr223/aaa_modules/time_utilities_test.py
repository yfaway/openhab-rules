import unittest
import time
import datetime
from org.slf4j import Logger, LoggerFactory
from core.testing import run_test

from aaa_modules import time_utilities
reload(time_utilities)
from aaa_modules import time_utilities

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for time_utilities.py.
class TimeUtilitiesTest(unittest.TestCase):
    def testKidsSleepTime_sleepTime_returnsTrue(self):
        dt = datetime.datetime(2018, 12, 25, 21, 58)
        self.assertTrue(time_utilities.isKidsSleepTime(time.mktime(dt.timetuple())))

    def testKidsSleepTime_saturdayNapTime_returnsTrue(self):
        dt = datetime.datetime(2018, 12, 22, 15, 10)
        self.assertTrue(time_utilities.isKidsSleepTime(time.mktime(dt.timetuple())))

    def testKidsSleepTime_sundayNapTime_returnsTrue(self):
        dt = datetime.datetime(2018, 12, 23, 15, 10)
        self.assertTrue(time_utilities.isKidsSleepTime(time.mktime(dt.timetuple())))

    def testKidsSleepTime_notSleepTime_returnsTrue(self):
        dt = datetime.datetime(2018, 12, 25, 10)
        self.assertFalse(time_utilities.isKidsSleepTime(time.mktime(dt.timetuple())))

    def testKidsSleepTime_weekdayAfternoon_returnsFalse(self):
        dt = datetime.datetime(2018, 12, 25, 15, 10)
        self.assertFalse(time_utilities.isKidsSleepTime(time.mktime(dt.timetuple())))

#run_test(TimeUtilitiesTest, logger) 

