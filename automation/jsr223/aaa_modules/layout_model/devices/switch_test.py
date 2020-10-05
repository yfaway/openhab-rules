import unittest

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device_test import MockedEventDispatcher

#from aaa_modules.layout_model.devices import switch
#reload(switch)
from aaa_modules.layout_model.devices.switch import Light

LIGHT_SWITCH_NAME = 'TestLightName'
TIMER_NAME = 'TestTimerName'

# Unit tests for switch.py.
class LightTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(LIGHT_SWITCH_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.lightItem = SwitchItem(LIGHT_SWITCH_NAME)
        scope.itemRegistry.add(self.lightItem)

        self.lightItem.setState(scope.OnOffType.OFF)

        self.light = Light(self.lightItem, 10)

    def tearDown(self):
        scope.itemRegistry.remove(self.lightItem.getName())

    def testTurnOn_lightWasOff_returnsExpected(self):
        self.light.turnOn(MockedEventDispatcher(scope.itemRegistry))
        self.assertEqual(scope.OnOffType.ON, self.lightItem.getState())

    def testTurnOn_lightWasAlreadyOn_timerIsRenewed(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.assertFalse(self.light._isTimerActive())

        self.light.turnOn(MockedEventDispatcher(scope.itemRegistry))
        self.assertEqual(scope.OnOffType.ON, self.lightItem.getState())
        self.assertTrue(self.light._isTimerActive())

    def testOnSwitchTurnedOn_validParams_timerIsTurnedOn(self):
        self.lightItem.setState(scope.OnOffType.ON)

        isProcessed = self.light.onSwitchTurnedOn(
                MockedEventDispatcher(scope.itemRegistry), self.lightItem.getName())
        self.assertTrue(isProcessed)
        self.assertTrue(self.light._isTimerActive())

    def testOnSwitchTurnedOn_invalidItemName_returnsFalse(self):
        isProcessed = self.light.onSwitchTurnedOn(
                MockedEventDispatcher(scope.itemRegistry), "wrong name")
        self.assertFalse(isProcessed)

    def testTurnOff_bothLightAndTimerOn_timerIsRenewed(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.light._startTimer(MockedEventDispatcher(scope.itemRegistry))
        self.assertTrue(self.light._isTimerActive())

        self.light.turnOff(MockedEventDispatcher(scope.itemRegistry))
        self.assertFalse(self.light._isTimerActive())

    def testOnSwitchTurnedOff_validParams_timerIsTurnedOn(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.light._startTimer(MockedEventDispatcher(scope.itemRegistry))

        isProcessed = self.light.onSwitchTurnedOff(
                MockedEventDispatcher(scope.itemRegistry), self.lightItem.getName())
        self.assertTrue(isProcessed)
        self.assertFalse(self.light._isTimerActive())

    def testOnSwitchTurnedOff_invalidItemName_returnsFalse(self):
        isProcessed = self.light.onSwitchTurnedOff(
                MockedEventDispatcher(scope.itemRegistry), "wrong name")
        self.assertFalse(isProcessed)

    def testIsLowIlluminance_noThresholdSet_returnsFalse(self):
        self.assertFalse(self.light.isLowIlluminance(10))

    def testIsLowIlluminance_currentIlluminanceNotAvailable_returnsFalse(self):
        self.light = Light(self.lightItem, 10, 50)
        self.assertFalse(self.light.isLowIlluminance(-1))

    def testIsLowIlluminance_currentIlluminanceAboveThreshold_returnsFalse(self):
        self.light = Light(self.lightItem, 10, 50)
        self.assertFalse(self.light.isLowIlluminance(60))

    def testIsLowIlluminance_currentIlluminanceBelowThreshold_returnsTrue(self):
        self.light = Light(self.lightItem, 10, 50)
        self.assertTrue(self.light.isLowIlluminance(10))

PE.runUnitTest(LightTest)
