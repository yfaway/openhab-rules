# This Python file uses the following encoding: utf-8
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.actions.range_violation_alert import RangeViolationAlert
from aaa_modules.layout_model.devices.temperature_sensor import TemperatureSensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

@action(events = [ZoneEvent.TEMPERATURE_CHANGED], devices = [TemperatureSensor])
class AlertOnTemperatureOutOfRange:

    '''
    Send an warning alert if the temperature is outside the range.
    @see RangeViolationAlert.
    '''

    def __init__(self, minTemperature = 16, maxTemperature = 30,
            notificationStepValue = 2):
        '''
        Ctor

        :param int minTemperature: the minimum temperature in percentage.
        :param int maxTemperature: the maximum temperature in percentage.
        :param int notificationStepValue: the value at which point a 
            notification email will be sent. E.g. with the default maxTemperature
            of 50 and the step value of 3, the first notification is at 53,
            and the next one is 56.
        :raise ValueError: if any parameter is invalid
        '''

        if minTemperature <= 0:
            raise ValueError('minTemperature must be positive')

        if maxTemperature <= 0:
            raise ValueError('maxTemperature must be positive')

        if maxTemperature <= minTemperature:
            raise ValueError('maxTemperature must be greater than minTemperature')

        if notificationStepValue <= 0:
            raise ValueError('notificationStepValue must be positive')

        self.rangeAlert = RangeViolationAlert(minTemperature, maxTemperature,
                notificationStepValue, "temperature", "°C", "TEMPERATURE", 30, False)

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        percentage = self.getFirstDevice(eventInfo).getTemperature()
        self.rangeAlert.updateState(percentage, zone, zoneManager)

        return True
