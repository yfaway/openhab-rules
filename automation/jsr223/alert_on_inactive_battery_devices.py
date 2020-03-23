from core.rules import rule
from core.triggers import when
from core.jsr223 import scope

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

THRESHOLD_IN_SECONDS = 3 * 24 * 3600 # 3 days

@rule("Check for battery device inactivity at specific interval")
@when("Time cron 0 0 20 1/3 * ? *")
def checkInactivity(event):
    inactiveDevices = getInactiveBatteryDevices(zm, THRESHOLD_IN_SECONDS)

    if len(inactiveDevices) > 0:
        subject = "{} inactive battery devices".format(len(inactiveDevices))
        body = "The following battery-powered devices haven't triggered "\
               "in the last {} hours\r\n  - ".format(THRESHOLD_IN_SECONDS / 3600)
        body += "\r\n  - ".join(inactiveDevices)

        alert = Alert.createInfoAlert(subject, body)
        if not AlertManager.processAdminAlert(alert):
            PE.logInfo('Failed to send inactive battery device alert')
    else:
        PE.logInfo("No inactive battery devices detected.")

def getInactiveBatteryDevices(zoneManager, thresholdInSeconds):
    '''
    :rtype: list(str) the list of inactive devices
    '''
    inactiveDeviceName = []
    for z in zoneManager.getZones():
        batteryDevices = [d for d in z.getDevices() if d.isBatteryPowered()]

        for d in batteryDevices:
            if not d.wasRecentlyActivated(thresholdInSeconds):
                inactiveDeviceName.append(
                        "{}: {}".format(z.getName(), d.getItemName()))

    return inactiveDeviceName

#checkInactivity(scope.event)
