import re
import time

from org.slf4j import Logger, LoggerFactory
from core.rules import rule
from core.triggers import when
from org.joda.time import DateTime

from org.eclipse.smarthome.model.script.actions.HTTP import sendHttpGetRequest

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class Forecast(object):
    def __init__(self, forecastTime, temperature, condition,
            precipationProbability, wind):
        self._forecastTime = forecastTime
        self._temperature = temperature
        self._condition = condition
        self._precipationProbability = precipationProbability
        self._wind = wind

    def getForecastTime(self):
        return self._forecastTime

    def getTemperature(self):
        return self._temperature
    
    def getCondition(self):
        return self._condition

    def getPrecipationProbability(self):
        return self._precipationProbability

    def getWind(self):
        return self._wind

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"{}: {}, {}, {}, {}".format(self.getForecastTime(),
                self.getTemperature(), self.getCondition(),
                self.getPrecipationProbability(), self.getWind())
        return str

def retrieveForecast(envCanadaUrl, hourCount = 10):
    data = sendHttpGetRequest(envCanadaUrl)

    timeStruct = time.localtime()
    hourOfDay = timeStruct[3]

    # create an array of hours to look up
    hourStrings = [] # e.g. 07:00, 21:00
    for increment in range(1, hourCount + 1):
        hour = (hourOfDay + increment) % 24
        hourString = ("0" + str(hour)) if hour < 10 else str(hour)
        hourString += ":00"

        hourStrings.append(hourString)


    pattern = r"""header2.*?\>(\d+)<             # temp 
                  .*?<p>(.*?)</p>                # condition
                  .*?header4.*?>(.+?)<           # precip probability
                  .*?abbr.*?>(.+?)</abbr> (.*?)< # wind direction and speed
        """
    forecasts = []
    index = 0
    for hourString in hourStrings:
        searchString = '<td headers="header1" class="text-center">{}</td>'.format(hourString)
        index = data.find(searchString, index)

        subdata = data[index:]
        match = re.search(pattern, subdata, 
                re.MULTILINE | re.DOTALL | re.VERBOSE)
        if not match:
            raise ValueError("Invalid pattern.")

        temperature = int(match.group(1))
        condition = match.group(2)
        precipProb = match.group(3)
        wind = u'' + match.group(5) + match.group(4)

        forecasts.append(Forecast(hourString, temperature, condition, precipProb, wind))

        logger.info("*** temp: {}".format(str(forecasts[-1])))

    return forecasts

retrieveForecast('https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html')
