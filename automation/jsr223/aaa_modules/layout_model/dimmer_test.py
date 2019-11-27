import unittest
import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

#from aaa_modules.layout_model import dimmer
#reload(dimmer)
from aaa_modules.layout_model.dimmer import Dimmer

DIMMER_NAME = 'TestDimmerName'
TIMER_NAME = 'TestTimerName'

# Unit tests for dimmer.py.
class DimmerTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(DIMMER_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.dimmerItem = DimmerItem(DIMMER_NAME)
        scope.itemRegistry.add(self.dimmerItem)

        self.timerItem = SwitchItem(TIMER_NAME)
        scope.itemRegistry.add(self.timerItem)

        self.dimmerItem.setState(scope.OnOffType.OFF)
        self.timerItem.setState(scope.OnOffType.OFF)

        self.dimmer = Dimmer(self.dimmerItem, self.timerItem, 100, "0-23:59")

    def tearDown(self):
        scope.itemRegistry.remove(self.dimmerItem.getName())
        scope.itemRegistry.remove(self.timerItem.getName())

    def testTurnOn_lightWasOffOutsideDimTimeRange_returnsExpected(self):
        timeStruct = time.localtime()
        hourOfDay = timeStruct[3]

        if hourOfDay >= 22: # handle 24-hour wrapping
            hourOfDay = 0

        dimLevel = 5
        timeRanges = "{}-{}".format(hourOfDay + 2, hourOfDay + 2)
        self.dimmer = Dimmer(self.dimmerItem, self.timerItem, dimLevel, timeRanges)

        self.dimmer.turnOn(scope.events)
        time.sleep(0.1)
        self.assertTrue(self.dimmer.isOn())
        self.assertEqual(100, self.dimmerItem.getState().intValue())
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testTurnOn_lightWasOffWithinDimTimeRange_returnsExpected(self):
        timeStruct = time.localtime()
        hourOfDay = timeStruct[3]

        dimLevel = 5
        nextHour = 0 if hourOfDay == 23 else hourOfDay + 1 # 24-hour wrapping
        timeRanges = "{}-{}".format(hourOfDay, nextHour)
        self.dimmer = Dimmer(self.dimmerItem, self.timerItem, dimLevel, timeRanges)

        self.dimmer.turnOn(scope.events)
        time.sleep(0.1)
        self.assertTrue(self.dimmer.isOn())
        self.assertEqual(dimLevel, self.dimmerItem.getState().intValue())
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testTurnOn_lightWasAlreadyOn_timerIsRenewed(self):
        self.dimmerItem.setState(PercentType(100))
        self.timerItem.setState(scope.OnOffType.OFF)

        self.dimmer.turnOn(scope.events)
        time.sleep(0.1)
        self.assertTrue(self.dimmer.isOn())
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testTurnOff_bothLightAndTimerOn_timerIsRenewed(self):
        self.dimmerItem.setState(PercentType(0))
        self.timerItem.setState(scope.OnOffType.ON)

        self.dimmer.turnOff(scope.events)
        time.sleep(0.1)
        self.assertFalse(self.dimmer.isOn())

PE.runUnitTest(DimmerTest)
