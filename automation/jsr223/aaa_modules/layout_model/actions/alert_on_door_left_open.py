from threading import Timer

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.devices.contact import Door
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class AlertOnExternalDoorLeftOpen(Action):

    '''
    Send an warning alert if a door on an external zone has been left open for
    a period of time.
    Triggered when a door is open (--> sart the timer), or when a door is
    closed (--> stop the timer)
    '''

    def __init__(self, maxElapsedTimeInSeconds = 15 * 60):
        '''
        Ctor

        :param int maxElapsedTimeInSeconds: the elapsed time in second since
            a door has been open, and at which point an alert will be sent
        :raise ValueError: if any parameter is invalid
        '''

        if maxElapsedTimeInSeconds <= 0:
            raise ValueError('maxElapsedTimeInSeconds must be positive')

        self.timers = {}
        self.maxElapsedTimeInSeconds = maxElapsedTimeInSeconds

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.CONTACT_OPEN, ZoneEvent.CONTACT_CLOSED]

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if not zone.isExternal():
            return False

        doors = zone.getDevicesByType(Door)
        if len(doors) == 0:
            return False

        def sendAlert():
            msg = 'The {} door has been opened for {} minutes.'.format(
                    zone.getName(), self.maxElapsedTimeInSeconds / 60)

            alert = Alert.createWarningAlert(msg)
            AlertManager.processAlert(alert, zoneManager)

        for door in doors:
            timer = self.timers[door] if door in self.timers else None

            if door.isOpen():
                if None != timer:
                    timer.cancel()
                    del self.timers[door]

                timer = Timer(self.maxElapsedTimeInSeconds, sendAlert)
                timer.start()
                self.timers[door] = timer
            else:
                if None != timer:
                    if timer.isAlive():
                        timer.cancel()
                    else: # alert door now closed if a warning was previous sent
                        msg = 'The {} door is now closed.'.format(zone.getName())
                        alert = Alert.createWarningAlert(msg)
                        AlertManager.processAlert(alert, zoneManager)

                    del self.timers[door]

        return True

    def hasRunningTimer(self):
        '''
        Returns true if at least one timer is running.
        '''
        return any(t.isAlive() for t in self.timers.values())
