import unittest

#from aaa_modules import environment_canada
#reload(environment_canada)
from aaa_modules.environment_canada import Forecast, EnvCanada
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

# Unit tests for environment_canada.py.
class EnvCanadaTest(unittest.TestCase):
    def testRetrieveHourlyForecast_hourCountAboveThreshold_throwsException(self):
        with self.assertRaises(ValueError) as cm:
            EnvCanada.retrieveHourlyForecast('Ottawa', 25)

        self.assertEqual("hourCount must be between 1 and 24.", cm.exception.args[0])

    def testRetrieveHourlyForecast_hourCountBelowThreshold_throwsException(self):
        with self.assertRaises(ValueError) as cm:
            EnvCanada.retrieveHourlyForecast('Ottawa', 0)

        self.assertEqual("hourCount must be between 1 and 24.", cm.exception.args[0])

    def testRetrieveHourlyForecast_invalidCity_throwsException(self):
        with self.assertRaises(ValueError) as cm:
            EnvCanada.retrieveHourlyForecast('blah')

        self.assertEqual("Can't map city name to URL for blah", cm.exception.args[0])

    def testRetrieveHourlyForecast_validCity_returnsForecast(self):
        forecasts = EnvCanada.retrieveHourlyForecast('Ottawa')
        self.assertTrue(len(forecasts) > 0)

        for forecast in forecasts:
            self.assertTrue(forecast.getForecastTime() >= 0)
            self.assertTrue(len(forecast.getCondition()) > 0)
            self.assertTrue(len(forecast.getPrecipationProbability()) > 0)

    def testRetrieveHourlyForecast_validUrl_returnsForecast(self):
        forecasts = EnvCanada.retrieveHourlyForecast(
                'https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html',
                24)
        self.assertEqual(24, len(forecasts))

        for forecast in forecasts:
            self.assertTrue(forecast.getForecastTime() >= 0)
            self.assertTrue(len(forecast.getCondition()) > 0)
            self.assertTrue(len(forecast.getPrecipationProbability()) > 0)

PE.runUnitTest(EnvCanadaTest)
