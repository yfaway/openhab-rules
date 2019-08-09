from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import StringItem

from aaa_modules.layout_model.device_test import DeviceTest

from aaa_modules.layout_model import astro_sensor
reload(astro_sensor)
from aaa_modules.layout_model.astro_sensor import AstroSensor

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

ITEMS = [StringItem('AstroSensorName')]

# Unit tests for astro_sensor.py.
class AstroSensorTest(DeviceTest):

    def setUp(self):
        super(AstroSensorTest, self).setUp()
        self.astroSensor = AstroSensor(self.getItems()[0])

    def getItems(self, resetState = False):
        if resetState:
            ITEMS[0].setState(StringType(AstroSensor.LIGHT_ON_TIMES[0]))

        return ITEMS

    def testIsLightOnTime_eveningTime_returnsTrue(self):
        for value in AstroSensor.LIGHT_ON_TIMES:
            ITEMS[0].setState(StringType(value))
            self.assertTrue(self.astroSensor.isLightOnTime())

    def testIsLightOnTime_dayTime_returnsFalse(self):
        invalidValues = ["MORNING", "DAY", "AFTERNOON"]
        for value in invalidValues:
            ITEMS[0].setState(StringType(value))
            self.assertFalse(self.astroSensor.isLightOnTime())

run_test(AstroSensorTest, logger) 
