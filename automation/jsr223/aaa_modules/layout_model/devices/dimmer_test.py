import unittest
import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import SwitchItem
from org.eclipse.smarthome.core.library.types import PercentType

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device_test import MockedEventDispatcher

#from aaa_modules.layout_model.devices import dimmer
#reload(dimmer)
from aaa_modules.layout_model.devices.dimmer import Dimmer

DIMMER_NAME = 'TestDimmerName'
TIMER_NAME = 'TestTimerName'

# Unit tests for dimmer.py.
class DimmerTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(DIMMER_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.dimmerItem = DimmerItem(DIMMER_NAME)
        scope.itemRegistry.add(self.dimmerItem)

        self.dimmerItem.setState(scope.OnOffType.OFF)

        self.dimmer = Dimmer(self.dimmerItem, 10, 100, "0-23:59")

    def tearDown(self):
        scope.itemRegistry.remove(self.dimmerItem.getName())

    def testTurnOn_lightWasOffOutsideDimTimeRange_returnsExpected(self):
        timeStruct = time.localtime()
        hourOfDay = timeStruct[3]

        if hourOfDay >= 22: # handle 24-hour wrapping
            hourOfDay = 0

        dimLevel = 5
        timeRanges = "{}-{}".format(hourOfDay + 2, hourOfDay + 2)
        self.dimmer = Dimmer(self.dimmerItem, 10, dimLevel, timeRanges)

        self.dimmer.turnOn(MockedEventDispatcher(scope.itemRegistry))
        self.assertTrue(self.dimmer.isOn())
        self.assertEqual(100, self.dimmerItem.getState().intValue())
        self.assertTrue(self.dimmer._isTimerActive())

    def testTurnOn_lightWasOffWithinDimTimeRange_returnsExpected(self):
        timeStruct = time.localtime()
        hourOfDay = timeStruct[3]

        dimLevel = 5
        nextHour = 0 if hourOfDay == 23 else hourOfDay + 1 # 24-hour wrapping
        timeRanges = "{}-{}".format(hourOfDay, nextHour)
        self.dimmer = Dimmer(self.dimmerItem, 10, dimLevel, timeRanges)

        self.dimmer.turnOn(MockedEventDispatcher(scope.itemRegistry))
        self.assertTrue(self.dimmer.isOn())
        self.assertEqual(dimLevel, self.dimmerItem.getState().intValue())
        self.assertTrue(self.dimmer._isTimerActive())

    def testTurnOn_lightWasAlreadyOn_timerIsRenewed(self):
        self.dimmerItem.setState(PercentType(100))

        self.dimmer.turnOn(MockedEventDispatcher(scope.itemRegistry))
        self.assertTrue(self.dimmer.isOn())
        self.assertTrue(self.dimmer._isTimerActive())

    def testTurnOff_bothLightAndTimerOn_timerIsRenewed(self):
        self.dimmerItem.setState(PercentType(0))

        self.dimmer.turnOff(MockedEventDispatcher(scope.itemRegistry))
        self.assertFalse(self.dimmer.isOn())

PE.runUnitTest(DimmerTest)
