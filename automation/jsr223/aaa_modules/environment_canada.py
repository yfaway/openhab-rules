import re
import time
import urllib2

# Represent the weather forecast.
class Forecast(object):
    def __init__(self, forecastTime, temperature, condition,
            precipationProbability, wind):
        self._forecastTime = forecastTime
        self._temperature = temperature
        self._condition = condition
        self._precipationProbability = precipationProbability
        self._wind = wind

    # Return the time string such as "09:00", or "22:00".
    def getForecastTime(self):
        return self._forecastTime

    # Return the temperature in Celcius.
    # @return int
    def getTemperature(self):
        return self._temperature
    
    # Return the weather condition.
    # @return string
    def getCondition(self):
        return self._condition

    # Return the precipation probability.
    # Possible values: High (70%+), Medium (60% - 70%), Low (< 40%), or Nil (0%).
    # @return string
    def getPrecipationProbability(self):
        return self._precipationProbability

    # Return the wind info such as "15 NW".
    # @return string
    def getWind(self):
        return self._wind

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        str = u"{}: {:7} {:25} {:6} {:6}".format(self.getForecastTime(),
                self.getTemperature(), self.getCondition(),
                self.getPrecipationProbability(), self.getWind())
        return str


class EnvCanada(object):
    # Retrieves today's forecast.
    # @param url string - the Environment Canada website
    #    'https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html'
    # @param hourCount int - the # of forecast hour to get, starting from
    #     the next hour relative to the current time.
    # @return list of Forecast objects
    @staticmethod
    def retrieveForecast(url, hourCount = 10):
        if hourCount > 24:
            raise ValueError("Forecast can only cover up to 24 hours.")
            
        #data = sendHttpGetRequest(url)
        data = urllib2.urlopen(url).read()
        data = unicode(data, 'utf-8')

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
            wind = u'' + match.group(5) + ' ' + match.group(4)

            forecasts.append(Forecast(hourString, temperature, condition, precipProb, wind))

        return forecasts
