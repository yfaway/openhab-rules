from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.types import DecimalType

from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model.devices import illuminance_sensor
#reload(illuminance_sensor)
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

ITEMS = [NumberItem('IlluminanceSensorName')]

# Unit tests for illuminance_sensor.py.
class IlluminanceSensorTest(DeviceTest):

    def setUp(self):
        super(IlluminanceSensorTest, self).setUp()
        self.illuminanceSensor = IlluminanceSensor(self.getItems()[0])

    def getItems(self, resetState = False):
        if resetState:
            ITEMS[0].setState(DecimalType(0))

        return ITEMS

    def testGetIlluminanceLevel_noParams_returnsValidValue(self):
        self.assertEqual(0, self.illuminanceSensor.getIlluminanceLevel())

        ITEMS[0].setState(DecimalType(50))
        self.assertEqual(50, self.illuminanceSensor.getIlluminanceLevel())

PE.runUnitTest(IlluminanceSensorTest)
