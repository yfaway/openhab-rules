import time
from aaa_modules.alert import *
from aaa_modules.alert_manager import *
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.security_manager  import SecurityManager as SM
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class AlertOnEntraceActivity(Action):
    '''
    Sends an alert if there is an entrace (porch/backyard) activity if the
    system is armed-away or if the activity is during the night.

    Play a TTS message if it is not yet sleep time.
    '''

    def onAction(self, events, zone, getZoneByIdFn):
        timeStruct = time.localtime()
        hour = timeStruct[3]

        PE.logInfo("**** in alert: {}".format(SM.isArmedAway()))

        if SM.isArmedAway() or (hour >= 1 and hour <= 6):
            PE.logInfo("**** sending a")
            msg = 'Activity detected at the {} area.'.format(zone.getName())
            alert = Alert.createInfoAlert(msg)

            AlertManager.processAlert(alert)
