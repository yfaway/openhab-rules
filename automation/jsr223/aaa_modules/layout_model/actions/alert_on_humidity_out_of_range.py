from aaa_modules.layout_model.zone import Level, ZoneEvent
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.actions.range_violation_alert import RangeViolationAlert
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

@action(events = [ZoneEvent.HUMIDITY_CHANGED], devices = [HumiditySensor],
        levels = [Level.FIRST_FLOOR], internal = True)
class AlertOnHumidityOutOfRange:

    '''
    Send an warning alert if the humidity is outside the range.
    @see RangeViolationAlert.
    '''

    def __init__(self, minHumidity = 35, maxHumidity = 50,
            notificationStepValue = 3):
        '''
        Ctor

        :param int minHumidity: the minimum humidity in percentage.
        :param int maxHumidity: the maximum humidity in percentage.
        :param int notificationStepValue: the value at which point a 
            notification email will be sent. E.g. with the default maxHumidity
            of 50 and the step value of 3, the first notification is at 53,
            and the next one is 56.
        :raise ValueError: if any parameter is invalid
        '''

        if minHumidity <= 0:
            raise ValueError('minHumidity must be positive')

        if maxHumidity <= 0:
            raise ValueError('maxHumidity must be positive')

        if maxHumidity <= minHumidity:
            raise ValueError('maxHumidity must be greater than minHumidity')

        if notificationStepValue <= 0:
            raise ValueError('notificationStepValue must be positive')

        self.rangeAlert = RangeViolationAlert(minHumidity, maxHumidity,
                notificationStepValue, "humidity", "%", "HUMIDITY", 60, True)

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        percentage = self.getFirstDevice(eventInfo).getHumidity()
        self.rangeAlert.updateState(percentage, zone, zoneManager)

        return True
