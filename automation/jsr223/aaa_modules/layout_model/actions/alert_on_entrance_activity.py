import time
from aaa_modules.alert import *
from aaa_modules.alert_manager import *
from aaa_modules.camera_utilities import retrieveSnapshotsFromFileSystem
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.devices.camera import Camera
from aaa_modules.security_manager  import SecurityManager as SM
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class AlertOnEntraceActivity(Action):
    '''
    Avoid false alarm by determing if the camera also detects motion (through
    images differential). If both the PIR sensor and the camera detect motions,
    sends an alert if the system is armed-away or if the activity is during
    the night.
    '''

    def onAction(self, events, zone, getZoneByIdFn):
        currentEpoch = time.time()

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

            #if SM.isArmedAway() or (hour >= 1 and hour <= 6):
            alert = Alert.createWarningAlert(msg, None, attachmentUrls)
            AlertManager.processAlert(alert)

            return True
        else:
            PE.logInfo("No images from {} camera.".format(zone.getName()))

        return False
