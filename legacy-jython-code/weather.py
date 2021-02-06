from core.rules import rule
from core.triggers import when

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.environment_canada import Forecast, EnvCanada
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

@rule("Send emails if it is raining today.")
@when("Time cron 0 20 6 ? * MON-FRI *")
@when("Time cron 0 0 8 ? * SAT,SUN *")
def alertIfRainInShortermForecast(event):
    forecasts = EnvCanada.retrieveHourlyForecast('Ottawa', 12)
    rainPeriods = [f for f in forecasts if \
                 'High' == f.getPrecipationProbability() or \
                 'Medium' == f.getPrecipationProbability()]
    if len(rainPeriods) > 0:
        if len(rainPeriods) == 1:
            subject = u"Possible precipation at {}".format(
                    rainPeriods[0].getUserFriendlyForecastTime())
        else:
            subject = u"Possible precipation from {} to {}".format(
                    rainPeriods[0].getUserFriendlyForecastTime(),
                    rainPeriods[-1].getUserFriendlyForecastTime())

        body = u'Forecasts:\n'
        body += u"{:5} {:7} {:25} {:6} {:6}\n".format('Hour: ', 'Celsius',
                'Condition', 'Prob.', 'Wind')
        for f in forecasts:
            body += unicode(f) + '\n'

        alert = Alert.createInfoAlert(subject, body)
        result = AlertManager.processAlert(alert, zm)
        if not result:
            PE.logInfo('Failed to send rain alert')
