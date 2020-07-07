from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

@action(events = [ZoneEvent.HUMIDITY_CHANGED], devices = [HumiditySensor])
class AlertOnHumidityOutOfRange:

    '''
    Send an warning alert if the humidity is outside the range.
    To avoid too many notification, a step value is used. The action tracks
    the next min/max threshold values. When the humdity crosses these threshold,
    a notificatio will be send.
    For example, with the default settings, notification is sent with humidty
    is at 53, 56, 59, and so on. When it goes down to below 50, a
    back-to-normal notifcation is sent. Apply in the same manner when the
    humidity is below the min threshold.
    '''

    def __init__(self, minHumidity = 35, maxHumidity = 50,
            notificationStepValue = 3):
        '''
        Ctor

        :param int minHumidity: the minimum humidity in percentage.
        :param int maxHumidity: the maximum humidity in percentage.
        :param int notificationStepValue: the value at which point a 
            notificatio email will be sent. E.g. with the default maxHumidity
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

        self.minHumidity = minHumidity
        self.maxHumidity = maxHumidity
        self.notificationStepValue = notificationStepValue

        self.resetStates();

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        percentage = self.getFirstDevice(eventInfo).getHumidity()

        alertMessage = ''
        if percentage <= self.nextMinNotificationThreshold:
            alertMessage = 'The {} humidity {}% is below the threshold of {}%.'.format(
                    zone.getName(), percentage, self.minHumidity)
            self.nextMinNotificationThreshold -= self.notificationStepValue
        elif percentage >= self.nextMaxNotificationThreshold:
            alertMessage = 'The {} humidity {}% is above the threshold of {}%.'.format(
                    zone.getName(), percentage, self.maxHumidity)
            self.nextMaxNotificationThreshold += self.notificationStepValue
        elif percentage >= self.minHumidity and percentage <= self.maxHumidity:
            if self.sentAlert: # send an info alert that humidity is back to normal
                self.resetStates()

                backToNormalMsg = 'The {} humidity {}% is back to the normal range ({}% - {}%).'.format(
                        zone.getName(), percentage, self.minHumidity, self.maxHumidity)
                alert = Alert.createInfoAlert(backToNormalMsg)
                AlertManager.processAdminAlert(alert)

        if alertMessage != '':
            alert = Alert.createWarningAlert(alertMessage, None, [], "HUMIDITY_CHANGED", 60)
            AlertManager.processAdminAlert(alert)
            self.sentAlert = True

        return True

    def resetStates(self):
        '''
        Resets the internal states including the next min/max notification
        thresholds in percentage.
        '''

        # in percentage
        self.nextMaxNotificationThreshold = self.maxHumidity + self.notificationStepValue
        self.nextMinNotificationThreshold = self.minHumidity - self.notificationStepValue

        self.sentAlert = False
