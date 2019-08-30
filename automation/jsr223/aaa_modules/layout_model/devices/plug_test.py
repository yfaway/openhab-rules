import time

from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import SwitchItem, NumberItem

from aaa_modules.layout_model.device_test import DeviceTest

from aaa_modules.layout_model.devices import plug
reload(plug)
from aaa_modules.layout_model.devices.plug import Plug

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

ITEMS = [SwitchItem('_Plug'), NumberItem('_Power')]

# Unit tests for plug.py.
class PlugTest(DeviceTest):

    def setUp(self):
        super(PlugTest, self).setUp()
        self.plug = Plug(self.getItems()[0], self.getItems()[1])

    def getItems(self, resetState = False):
        if resetState:
            ITEMS[0].setState(scope.OnOffType.OFF)
            ITEMS[1].setState(DecimalType(100))

        return ITEMS

    def testIsOn_notOn_returnsFalse(self):
        self.assertFalse(self.plug.isOn())

    def testTurnOn_withScopeEvents_returnsTrue(self):
        self.plug.turnOn(scope.events)
        time.sleep(0.1)

        self.assertTrue(self.plug.isOn())
        self.assertEqual(100, self.plug.getWattage())

    def testTurnOff_withScopeEvents_returnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.ON)
        self.assertTrue(self.plug.isOn())

        self.plug.turnOff(scope.events)
        time.sleep(0.1)
        self.assertFalse(self.plug.isOn())

run_test(PlugTest, logger) 
