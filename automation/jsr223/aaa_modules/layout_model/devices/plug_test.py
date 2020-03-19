import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem, NumberItem
from org.eclipse.smarthome.core.library.types import DecimalType
from org.eclipse.smarthome.core.library.types import OnOffType

from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model.devices import plug
#reload(plug)
from aaa_modules.layout_model.devices.plug import Plug
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

ITEMS = [SwitchItem('_Plug'), NumberItem('_Power')]

# Unit tests for plug.py.
class PlugTest(DeviceTest):

    def setUp(self):
        super(PlugTest, self).setUp()
        self.plug = Plug(self.getItems()[0], self.getItems()[1])

    def getItems(self, resetState = False):
        if resetState:
            ITEMS[0].setState(OnOffType.OFF)
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
        ITEMS[0].setState(OnOffType.ON)
        self.assertTrue(self.plug.isOn())

        self.plug.turnOff(scope.events)
        time.sleep(0.1)
        self.assertFalse(self.plug.isOn())

PE.runUnitTest(PlugTest)
