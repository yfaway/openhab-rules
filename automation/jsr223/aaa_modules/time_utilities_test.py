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

    def testIsInTimeRange_noRange_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists([])

        self.assertEqual('Must have at least one time range.', cm.exception.args[0])

    def testIsInTimeRange_none_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists(None)

        self.assertEqual('Must have at least one time range.', cm.exception.args[0])

    def testIsInTimeRange_sameHour_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertTrue(time_utilities.isInTimeRange('7',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeSameHour_returnFalse(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertFalse(time_utilities.isInTimeRange('8',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeLargerThanEndMinute_returnFalse(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertFalse(time_utilities.isInTimeRange('8 - 8:30',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_noEndMinute_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertTrue(time_utilities.isInTimeRange('7 - 8',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeNoEndMinute_returnFalse(self):
        dt = datetime.datetime(2018, 12, 25, 8, 58)
        self.assertFalse(time_utilities.isInTimeRange('7-8',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_wrapAround_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertTrue(time_utilities.isInTimeRange('21 - 9',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_wrapAround2_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 18, 22)
        self.assertTrue(time_utilities.isInTimeRange('18 - 7',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeWrapAround1_returnFalse(self):
        dt = datetime.datetime(2018, 12, 25, 10, 58)
        self.assertFalse(time_utilities.isInTimeRange('21 - 9',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeWrapAround2_returnFalse(self):
        dt = datetime.datetime(2018, 12, 25, 20, 58)
        self.assertFalse(time_utilities.isInTimeRange('21 - 9',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_multipleRanges_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 7, 58)
        self.assertTrue(time_utilities.isInTimeRange('4-5, 7- 8',
                    time.mktime(dt.timetuple())))

    def testIsInTimeRange_negativeMultipleRanges_returnTrue(self):
        dt = datetime.datetime(2018, 12, 25, 10, 58)
        self.assertFalse(time_utilities.isInTimeRange('4-5, 8',
                    time.mktime(dt.timetuple())))

    def testStringToTimeRangeLists_noRange_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists('')

        self.assertEqual('Must have at least one time range.', cm.exception.args[0])

    def testStringToTimeRangeLists_none_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists(None)

        self.assertEqual('Must have at least one time range.', cm.exception.args[0])

    def testStringToTimeRangeLists_wrongFormat_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists('9, 3:2:3-5')

        self.assertEqual('Must be in format "HH" or "HH:MM".', cm.exception.args[0])

    def testStringToTimeRangeLists_invalidHour_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists('24')

        self.assertEqual('Hour must be between 0 and 23 inclusive.', cm.exception.args[0])

    def testStringToTimeRangeLists_invalidMinute_throwsError(self):
        with self.assertRaises(ValueError) as cm:
            time_utilities._stringToTimeRangeLists('7 - 8:60')

        self.assertEqual('Minute must be between 0 and 59 inclusive.', cm.exception.args[0])

    def testStringToTimeRangeLists_oneRangeWithSameHourNoMinutes_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("7")
        self.assertEqual(1, len(list))
        self.assertEqual([7, 0, 7, 59], list[0])

    def testStringToTimeRangeLists_oneRangeWithDiffHourNoMinutes_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("7 - 12")
        self.assertEqual(1, len(list))
        self.assertEqual([7, 0, 12, 0], list[0])

    def testStringToTimeRangeLists_oneRangeWithDiffHourPartialMinutes_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("7:10 - 12")
        self.assertEqual(1, len(list))
        self.assertEqual([7, 10, 12, 0], list[0])

    def testStringToTimeRangeLists_oneRangeWithDiffHourMinutes_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("7:10 - 12:30")
        self.assertEqual(1, len(list))
        self.assertEqual([7, 10, 12, 30], list[0])

    def testStringToTimeRangeLists_wrapAroundHour_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("21 - 7")
        self.assertEqual(1, len(list))
        self.assertEqual([21, 0, 7, 0], list[0])

    def testStringToTimeRangeLists_multipleRanges_returnsExpected(self):
        list = time_utilities._stringToTimeRangeLists("7:10 - 8:30, 9, 13 - 15, 16-17:30")
        self.assertEqual(4, len(list))
        self.assertEqual([7, 10, 8, 30], list[0])
        self.assertEqual([9, 0, 9, 59], list[1])
        self.assertEqual([13, 0, 15, 0], list[2])
        self.assertEqual([16, 0, 17, 30], list[3])

#run_test(TimeUtilitiesTest, logger) 
