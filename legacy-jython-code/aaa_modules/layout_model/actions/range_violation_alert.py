from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager

class RangeViolationAlert:
    '''
    Given a valid value range, track the state of the value, and send an warning
    alert when the value is out of range. Send another info alert when the
    value is back to the normal range.
    '''

    def __init__(self, minValue, maxValue, notificationStepValue = 3,
            label = "value", unit = "", module = None,
            intervalBetweenAlertsInMinutes = -1, adminAlert = False):
        '''
        Ctor
        :param int minValue: the minimum good value
        :param int maxValue: the maximum good value
        :param int notificationStepValue: the value at which point a 
            notification email will be sent. E.g. with the default maxValue
            of 50 and the step value of 3, the first notification is at 53,
            and the next one is 56.
        :param str label: the name of the value
        :param str unit: the unit of the value
        :raise ValueError: if any parameter is invalid
        '''
        if maxValue <= minValue:
            raise ValueError('maxValue must be greater than minValue')

        if notificationStepValue <= 0:
            raise ValueError('notificationStepValue must be positive')

        self.minValue = minValue
        self.maxValue = maxValue
        self.notificationStepValue = notificationStepValue
        self.label = label
        self.unit = unit
        self.module = module
        self.intervalBetweenAlertsInMinutes = intervalBetweenAlertsInMinutes
        self.adminAlert = adminAlert

        self.resetStates();

    def updateState(self, value, zone, zoneManager):
        '''
        Update this object with the latest value.
        If the value is outside the range, an warning alert will be sent.
        If the value is back to the normal range, an info alert will be sent.
        '''
        if value >= self.minValue and value <= self.maxValue:
            if self.sentAlert: # send an info alert that the value is back to normal
                self.resetStates()

                msg = 'The {} {} at {}{} is back to the normal range ({}% - {}%).'.format(
                        zone.getName(), self.label, value, self.unit,
                        self.minValue, self.maxValue)
                alert = Alert.createInfoAlert(msg)

                if self.adminAlert:
                    AlertManager.processAdminAlert(alert)
                else:
                    AlertManager.processAlert(alert)

        else:
            alertMessage = ''
            if value <= self.nextMinNotificationThreshold:
                alertMessage = 'The {} {} at {}{} is below the threshold of {}%.'.format(
                        zone.getName(), self.label, value, self.unit, self.minValue)
                self.nextMinNotificationThreshold -= self.notificationStepValue
            elif value >= self.nextMaxNotificationThreshold:
                alertMessage = 'The {} {} at {}{} is above the threshold of {}%.'.format(
                        zone.getName(), self.label, value, self.unit, self.maxValue)
                self.nextMaxNotificationThreshold += self.notificationStepValue

            if alertMessage != '':
                alert = Alert.createWarningAlert(alertMessage, None, [], 
                        self.module, self.intervalBetweenAlertsInMinutes)
                if self.adminAlert:
                    AlertManager.processAdminAlert(alert)
                else:
                    AlertManager.processAlert(alert)

                self.sentAlert = True

    def resetStates(self):
        '''
        Resets the internal states including the next min/max notification
        thresholds.
        '''

        self.nextMaxNotificationThreshold = self.maxValue + self.notificationStepValue
        self.nextMinNotificationThreshold = self.minValue - self.notificationStepValue

        self.sentAlert = False

