from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import NumberItem

from aaa_modules.layout_model import device_test
reload(device_test)
from aaa_modules.layout_model.device_test import DeviceTest

from aaa_modules.layout_model import illuminance_sensor
reload(illuminance_sensor)
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

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

run_test(IlluminanceSensorTest, logger) 
