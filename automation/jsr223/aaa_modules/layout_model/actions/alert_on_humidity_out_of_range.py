from threading import Timer

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import Action
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class AlertOnHumidityOutOfRange(Action):

    '''
    Send an warning alert if the humidity is outside the range.
    '''

    def __init__(self, minHumidity = 35, maxHumidity = 55):
        '''
        Ctor

        :param int minHumidity: the minimum humidity in percentage.
        :param int maxHumidity: the maximum humidity in percentage.
        :raise ValueError: if any parameter is invalid
        '''

        if minHumidity <= 0:
            raise ValueError('minHumidity must be positive')

        if maxHumidity <= 0:
            raise ValueError('maxHumidity must be positive')

        if maxHumidity <= minHumidity:
            raise ValueError('maxHumidity must be greater than minHumidity')

        self.minHumidity = minHumidity
        self.maxHumidity = maxHumidity
        self.sentAlert = False

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.HUMIDITY_CHANGED]

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if zone.isExternal():
            return False

        humiditySensors = zone.getDevicesByType(HumiditySensor)
        if len(humiditySensors) == 0:
            return False

        percentage = humiditySensors[0].getHumidity()

        msg = ''
        if percentage <= self.minHumidity:
            msg = 'The {} humidity {}% is below the threshold of {}%.'.format(
                    zone.getName(), percentage, self.minHumidity)
        elif percentage >= self.maxHumidity:
            msg = 'The {} humidity {}% is above the threshold of {}%.'.format(
                    zone.getName(), percentage, self.maxHumidity)

        if msg == '': # send an info alert that humidity is back to normal
            if self.sentAlert:
                self.sentAlert = False

                msg = 'The {} humidity {}% is back to the normal range ({}% - {}%).'.format(
                        zone.getName(), percentage, self.minHumidity, self.maxHumidity)
                alert = Alert.createInfoAlert(msg)
                AlertManager.processAlert(alert, zoneManager)
        else:
            alert = Alert.createWarningAlert(msg, None, [], "HUMIDITY_CHANGED", 60)
            AlertManager.processAlert(alert, zoneManager)

            self.sentAlert = True

        return True
