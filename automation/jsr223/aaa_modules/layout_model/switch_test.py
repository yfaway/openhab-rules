import unittest

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device_test import MockedEventDispatcher

#from aaa_modules.layout_model import switch
#reload(switch)
from aaa_modules.layout_model.switch import Light

LIGHT_SWITCH_NAME = 'TestLightName'
TIMER_NAME = 'TestTimerName'

# Unit tests for switch.py.
class LightTest(unittest.TestCase):

    def setUp(self):
        scope.itemRegistry.remove(LIGHT_SWITCH_NAME)
        scope.itemRegistry.remove(TIMER_NAME)

        self.lightItem = SwitchItem(LIGHT_SWITCH_NAME)
        scope.itemRegistry.add(self.lightItem)

        self.timerItem = SwitchItem(TIMER_NAME)
        scope.itemRegistry.add(self.timerItem)

        self.lightItem.setState(scope.OnOffType.OFF)
        self.timerItem.setState(scope.OnOffType.OFF)

        self.light = Light(self.lightItem, self.timerItem)

    def tearDown(self):
        scope.itemRegistry.remove(self.lightItem.getName())
        scope.itemRegistry.remove(self.timerItem.getName())

    def testTurnOn_lightWasOff_returnsExpected(self):
        self.light.turnOn(MockedEventDispatcher())
        self.assertEqual(scope.OnOffType.ON, self.lightItem.getState())

    def testTurnOn_lightWasAlreadyOn_timerIsRenewed(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.timerItem.setState(scope.OnOffType.OFF)

        self.light.turnOn(MockedEventDispatcher())
        self.assertEqual(scope.OnOffType.ON, self.lightItem.getState())
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testOnSwitchTurnedOn_validParams_timerIsTurnedOn(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.timerItem.setState(scope.OnOffType.OFF)

        isProcessed = self.light.onSwitchTurnedOn(
                MockedEventDispatcher(), self.lightItem.getName())
        self.assertTrue(isProcessed)
        self.assertEqual(scope.OnOffType.ON, self.timerItem.getState())

    def testOnSwitchTurnedOn_invalidItemName_returnsFalse(self):
        isProcessed = self.light.onSwitchTurnedOn(
                MockedEventDispatcher(), "wrong name")
        self.assertFalse(isProcessed)

    def testTurnOff_bothLightAndTimerOn_timerIsRenewed(self):
        self.lightItem.setState(scope.OnOffType.ON)
        self.timerItem.setState(scope.OnOffType.ON)

        self.light.turnOff(MockedEventDispatcher())
        self.assertEqual(scope.OnOffType.OFF, self.lightItem.getState())

    def testOnSwitchTurnedOff_validParams_timerIsTurnedOn(self):
        self.lightItem.setState(scope.OnOffType.OFF)
        self.timerItem.setState(scope.OnOffType.ON)

        isProcessed = self.light.onSwitchTurnedOff(
                MockedEventDispatcher(), self.lightItem.getName())
        self.assertTrue(isProcessed)
        self.assertEqual(scope.OnOffType.OFF, self.timerItem.getState())

    def testOnSwitchTurnedOff_invalidItemName_returnsFalse(self):
        isProcessed = self.light.onSwitchTurnedOff(
                MockedEventDispatcher(), "wrong name")
        self.assertFalse(isProcessed)

    def testIsLowIlluminance_noThresholdSet_returnsFalse(self):
        self.assertFalse(self.light.isLowIlluminance(10))

    def testIsLowIlluminance_currentIlluminanceNotAvailable_returnsFalse(self):
        self.light = Light(self.lightItem, self.timerItem, 50)
        self.assertFalse(self.light.isLowIlluminance(-1))

    def testIsLowIlluminance_currentIlluminanceAboveThreshold_returnsFalse(self):
        self.light = Light(self.lightItem, self.timerItem, 50)
        self.assertFalse(self.light.isLowIlluminance(60))

    def testIsLowIlluminance_currentIlluminanceBelowThreshold_returnsTrue(self):
        self.light = Light(self.lightItem, self.timerItem, 50)
        self.assertTrue(self.light.isLowIlluminance(10))

PE.runUnitTest(LightTest)
