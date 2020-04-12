from threading import Timer

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import Action
from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition
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

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.CONTACT_CLOSED]

    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

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
                    # Don't know why list comprehension version like below 
                    # doesn't work, Jython just hang on this statement:
                    # if not any(z.isOccupied(elapsedTime) for z in zoneManager.getZones()):
                    # Below is a work around.
                    occupied = False
                    activeDevice = None

                    for z in zoneManager.getZones():
                        if z.isExternal():
                            continue

                        # motion sensor switches off after around 3', need to
                        # that into account.
                        motionDelayInSec = 3 * 60
                        delayTimeInSec = self.maxElapsedTimeInSeconds + motionDelayInSec

                        (occupied, activeDevice) = z.isOccupied( delayTimeInSec)
                        if occupied:
                            break

                    if occupied:
                        PE.logInfo('Auto-arm cancelled (activities detected @ {}).'.format(
                                    activeDevice))
                    else:
                        securityPartitions[0].armAway(events)

                        msg = 'The house has been automatically armed-away (front door closed and no activity)'
                        alert = Alert.createWarningAlert(msg)
                        AlertManager.processAlert(alert, zoneManager)

                self.timer = Timer(self.maxElapsedTimeInSeconds, armAndSendAlert)
                self.timer.start()

        return True
