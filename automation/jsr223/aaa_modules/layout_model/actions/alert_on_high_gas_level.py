from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.zone import Level, ZoneEvent
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.devices.gas_sensor import GasSensor
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

@action(events = [ZoneEvent.GAS_TRIGGER_STATE_CHANGED], devices = [GasSensor])
class AlertOnHighGasLevel:

    '''
    Send a critical alert if the gas sensor is triggered (i.e. the reading
    is above the threshold).
    '''

    def __init__(self, intervalBetweenAlertsInMinutes = 15):
        '''
        Ctor

        :raise ValueError: if any parameter is invalid
        '''
        if intervalBetweenAlertsInMinutes <= 0:
            raise ValueError('intervalBetweenAlertsInMinutes must be positive')

        self.intervalBetweenAlertsInMinutes = intervalBetweenAlertsInMinutes
        self.notifiedForGasType = {} # mapped from gas type to boolean

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()

        gasSensor = zone.getDeviceByEvent(eventInfo)
        gasType = gasSensor.__class__.__name__

        if gasSensor.isTriggered():
            self.notifiedForGasType[gasType] = True
            alertMessage = 'The {} {} at {} is above normal level.'.format(
                    zone.getName(), gasType, gasSensor.getValue())
            alert = Alert.createCriticalAlert(alertMessage, None, [], 
                    gasType, self.intervalBetweenAlertsInMinutes)
            AlertManager.processAlert(alert)

        else:
            if gasType in self.notifiedForGasType:
                alertMessage = 'The {} {} is back to normal.'.format(
                        zone.getName(), gasType)
                alert = Alert.createInfoAlert(alertMessage)
                AlertManager.processAlert(alert)

                del self.notifiedForGasType[gasType]

        return True
