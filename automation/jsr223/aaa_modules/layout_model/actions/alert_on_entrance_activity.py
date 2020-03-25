import time
from aaa_modules.alert import *
from aaa_modules.alert_manager import *
from aaa_modules.camera_utilities import retrieveSnapshotsFromFileSystem
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import Action
from aaa_modules.layout_model.devices.camera import Camera
from aaa_modules.layout_model.devices.contact import Door
from aaa_modules.security_manager  import SecurityManager as SM
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class AlertOnEntraceActivity(Action):
    '''
    The alert is triggered from a PIR motion sensor. The motion sensor
    sometimes generate false positive event. This is remedied by determing if
    the camera also detects motion (through the image differential). If both
    the PIR sensor and the camera detect motions, sends an alert if the system
    is armed-away or if the activity is during the night.

    The alert is suppressed if the zone's door was just opened. This indicates
    the occupant walking out of the house, and thus shouldn't triggered the
    event.
    '''

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.MOTION]

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        currentEpoch = time.time()

        doorOpenPeriodInSeconds = 10
        for door in zone.getDevicesByType(Door):
            if door.wasRecentlyActivated(doorOpenPeriodInSeconds):
                PE.logInfo("A door was just open for zone {}; ignore motion event.".format(
                            zone.getName()))
                return


        cameras = zone.getDevicesByType(Camera)
        if len(cameras) == 0:
            PE.logInfo("No camera found for zone {}".format(zone.getName()))
            return

        camera = cameras[0]
        if not camera.hasMotionEvent():
            PE.logInfo("Camera doesn't indicate motion event; likely a false positive PIR event.")
            return

        time.sleep(10) # wait for a bit to retrieve more images

        offsetSeconds = 5
        maxNumberOfSeconds = 15
        attachmentUrls = camera.getSnapshotUrls(currentEpoch,
                maxNumberOfSeconds, offsetSeconds)

        if len(attachmentUrls) > 0:
            timeStruct = time.localtime()
            hour = timeStruct[3]

            msg = 'Activity detected at the {} area.'.format(
                    zone.getName(), len(attachmentUrls))

            if SM.isArmedAway() or hour <= 6:
                alert = Alert.createWarningAlert(msg, None, attachmentUrls)
            else:
                alert = Alert.createAudioWarningAlert(msg)

            AlertManager.processAlert(alert)

            return True
        else:
            PE.logInfo("No images from {} camera.".format(zone.getName()))

        return False
