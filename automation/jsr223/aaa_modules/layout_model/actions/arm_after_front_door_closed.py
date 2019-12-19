from threading import Timer

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.alarm_partition import AlarmPartition
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.devices.contact import Door
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class ArmAfterFrontDoorClosed(Action):

    '''
    Automatically arm the house if a front door was closed and there was no
    activity in the house for x number of seconds.
    Once armed, an alert will be sent out.
    '''

    def __init__(self, maxElapsedTimeInSeconds = 15 * 60):
        '''
        Ctor

        :param int maxElapsedTimeInSeconds: the elapsed time in second since
            a door has been closed at which point the timer will determine if
            there was any previous activity in the house. If not, the security
            system is armed.
        :raise ValueError: if any parameter is invalid
        '''

        if maxElapsedTimeInSeconds <= 0:
            raise ValueError('maxElapsedTimeInSeconds must be positive')

        self.timer = None
        self.maxElapsedTimeInSeconds = maxElapsedTimeInSeconds

    def onAction(self, events, zone, zoneManager):
        if not zone.isExternal():
            return False

        if zone.getName() == "Patio": # todo: add Zone::isBack()
            return False

        doors = zone.getDevicesByType(Door)
        if len(doors) == 0:
            return False

        securityPartitions = zoneManager.getDevicesByType(AlarmPartition)
        if len(securityPartitions) == 0:
            return False

        if not securityPartitions[0].isUnarmed():
            return False

        for door in doors:
            if door.isClosed():
                if None != self.timer:
                    self.timer.cancel()

                def armAndSendAlert():

                    occupiedZones = [
                        z.isOccupied(self.maxElapsedTimeInSeconds) for z in zoneManager.getZones()]
                    if not any(occupiedZones):
                        securityPartitions[0].armAway(events)

                        msg = 'The house has been automatically armed-away'
                        alert = Alert.createWarningAlert(msg)
                        AlertManager.processAlert(alert)

                self.timer = Timer(self.maxElapsedTimeInSeconds, armAndSendAlert)
                self.timer.start()

        return True
