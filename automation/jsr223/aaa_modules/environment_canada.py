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

    # Return the hour in 24-hour format.
    # @return int
    def getForecastTime(self):
        return self._forecastTime

    # Returns the forecast hour in user friendly format (1AM, 2PM,...)
    # @return string
    def getUserFriendlyForecastTime(self):
        hour = self._forecastTime

        if hour == 0:
            return 'Midnight'
        elif hour < 12:
            return str(hour) + ' AM'
        elif hour == 12:
            return 'Noon'
        else:
            return str(hour - 12) + ' PM'

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
        str = u"{:5}: {:7} {:25} {:6} {:6}".format(self.getForecastTime(),
                self.getTemperature(), self.getCondition(),
                self.getPrecipationProbability(), self.getWind())
        return str


class EnvCanada(object):
    # Mapping from lowercase city name to the env canada identifier.
    CITY_FORECAST_MAPPING = { 'ottawa' : 'on-118' }

    # Retrieves the hourly forecast for the given city.
    # @param cityOrUrl string - the city name or the Environment Canada website
    #    'https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html'
    # @param hourCount int - the # of forecast hour to get, starting from
    #     the next hour relative to the current time.
    # @return list of Forecast objects
    # @throw ValueError if cityOrUrl points to an invalid city, or if 
    #     hourCount is more than 24 and less than 1.
    @staticmethod
    def retrieveHourlyForecast(cityOrUrl, hourCount = 12):
        if hourCount > 24 or hourCount < 1:
            raise ValueError("hourCount must be between 1 and 24.")

        if cityOrUrl[0:6].lower() != 'https:':
            normalizedCity = cityOrUrl.lower()
            if normalizedCity not in EnvCanada.CITY_FORECAST_MAPPING:
                raise ValueError(
                        "Can't map city name to URL for {}".format(cityOrUrl))

            url = 'https://www.weather.gc.ca/forecast/hourly/{}_metric_e.html'.format(
                EnvCanada.CITY_FORECAST_MAPPING[normalizedCity])
        else:
            url = cityOrUrl
            
        data = urllib2.urlopen(url).read()
        data = unicode(data, 'utf-8')

        timeStruct = time.localtime()
        hourOfDay = timeStruct[3]

        pattern = r"""header2.*?\>(\d+)<             # temp 
                      .*?<p>(.*?)</p>                # condition
                      .*?header4.*?>(.+?)<           # precip probability
                      .*?abbr.*?>(.+?)</abbr> (.*?)< # wind direction and speed
            """
        forecasts = []
        index = 0
        for increment in range(1, hourCount + 1):
            hour = (hourOfDay + increment) % 24
            hourString = ("0" + str(hour)) if hour < 10 else str(hour)
            hourString += ":00"

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

            forecasts.append(Forecast(hour, temperature, condition, precipProb, wind))

        return forecasts
