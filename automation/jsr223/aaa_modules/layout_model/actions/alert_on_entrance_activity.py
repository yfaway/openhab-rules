import time
from aaa_modules.alert import *
from aaa_modules.alert_manager import *
from aaa_modules.camera_utilities import retrieveSnapshotsFromFileSystem
from aaa_modules.layout_model.actions.action import Action
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

        time.sleep(20) # wait for a bit to retrieve more images

        offsetSeconds = 5
        maxNumberOfSeconds = 15
        attachmentUrls = retrieveSnapshotsFromFileSystem(
                maxNumberOfSeconds, offsetSeconds, currentEpoch,
                zone.getName())

        if len(attachmentUrls) > 0:
            timeStruct = time.localtime()
            hour = timeStruct[3]

            if SM.isArmedAway() or (hour >= 1 and hour <= 6):
                msg = 'Activity detected at the {} area.'.format(
                        zone.getName(), len(attachmentUrls))

                alert = Alert.createInfoAlert(msg, None, attachmentUrls)

                AlertManager.processAlert(alert)

                return True
        else:
            PE.logInfo("No images from {} camera.".format(zone.getName()))

        return False
