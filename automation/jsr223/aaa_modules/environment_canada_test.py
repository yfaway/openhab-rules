import unittest

from org.slf4j import Logger, LoggerFactory
from core.testing import run_test

from aaa_modules import environment_canada
reload(environment_canada)
from aaa_modules.environment_canada import Forecast, EnvCanada

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for environment_canada.py.
class EnvCanadaTest(unittest.TestCase):

    def testRetrieveForecast_validUrl_returnsTrue(self):
        forecasts = EnvCanada.retrieveForecast(
                'https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html',
                24)
        self.assertEqual(24, len(forecasts))

        for forecast in forecasts:
            self.assertTrue(len(forecast.getCondition()) > 0)
            self.assertTrue(len(forecast.getPrecipationProbability()) > 0)

run_test(EnvCanadaTest, logger) 
