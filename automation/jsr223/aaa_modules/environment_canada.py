'''
An utility class to retrieve the weather forecast from the Environment Canada
service.
https://www.weather.gc.ca/forecast/
'''

import re
import time
import urllib2

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class Forecast(object):
    '''
    Represent the weather forecast.
    '''

    def __init__(self, forecastTime, temperature, condition,
            precipationProbability, wind):
        self._forecastTime = forecastTime
        self._temperature = temperature
        self._condition = condition
        self._precipationProbability = precipationProbability
        self._wind = wind

    def getForecastTime(self):
        '''
        Return the hour in 24-hour format.

        :rtype: int
        '''
        return self._forecastTime

    def getUserFriendlyForecastTime(self):
        '''
        Returns the forecast hour in user friendly format (1AM, 2PM,...)

        :rtype: str
        '''

        hour = self._forecastTime

        if hour == 0:
            return 'Midnight'
        elif hour < 12:
            return str(hour) + ' AM'
        elif hour == 12:
            return 'Noon'
        else:
            return str(hour - 12) + ' PM'

    def getTemperature(self):
        '''
        Return the temperature in Celcius.

        :rtype: int
        '''
        return self._temperature
    
    def getCondition(self):
        '''
        Return the weather condition.

        :rtype: str
        '''
        return self._condition

    def getPrecipationProbability(self):
        '''
        Return the precipation probability.
        Possible values: High (70%+), Medium (60% - 70%), Low (< 40%), or Nil (0%).

        :rtype: str
        '''
        return self._precipationProbability

    def getWind(self):
        '''
        Return the wind info such as "15 NW".

        :rtype: str
        '''
        return self._wind

    def __str__(self):
        '''
        :rtype: str
        '''
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        '''
        :rtype: unicode
        '''
        str = u"{:5}: {:7} {:25} {:6} {:6}".format(self.getForecastTime(),
                self.getTemperature(), self.getCondition(),
                self.getPrecipationProbability(), self.getWind())
        return str


class EnvCanada(object):
    '''
    Utility class to retreive the hourly forecast.
    '''


    CITY_FORECAST_MAPPING = { 'ottawa' : 'on-118' }
    '''
    Mapping from lowercase city name to the env canada identifier.
    '''

    @staticmethod
    def retrieveHourlyForecast(cityOrUrl, hourCount = 12):
        '''
        Retrieves the hourly forecast for the given city.

        :param str cityOrUrl: the city name or the Environment Canada website\
            'https://www.weather.gc.ca/forecast/hourly/on-118_metric_e.html'
        :param int hourCount: the # of forecast hour to get, starting from \
            the next hour relative to the current time.
        :rtype: list(Forecast)
        :raise: ValueError if cityOrUrl points to an invalid city, or if \
            hourCount is more than 24 and less than 1.
        '''
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

        pattern = r"""header2.*?\>(-?\d+)<           # temp 
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
