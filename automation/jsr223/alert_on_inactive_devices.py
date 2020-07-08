from core.rules import rule
from core.triggers import when
from core.jsr223 import scope

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

INACTIVE_BATTERY_DEVICES_THRESHOLD_IN_SECONDS = 3 * 24 * 3600 # 3 days

INACTIVE_AUTOREPORT_WIFI_DEVICES_THRESHOLD_IN_SECONDS = 12 * 3600 # 12 hours

@rule("Check inactive battery device every 3 days")
@when("Time cron 0 0 20 1/3 * ? *")
def checkInactivity(event):
    _checkAndSendAlert(zm, getInactiveBatteryDevices,
            "battery",
            INACTIVE_BATTERY_DEVICES_THRESHOLD_IN_SECONDS)

rule("Check for inactive auto-report WiFi devices every 12 hours")
@when("Time cron 0 0 0/12 ? * * *")
def checkInactiveAutoReportWifiDevices(event):
    _checkAndSendAlert(zm, getInactiveAutoReportWifiDevices,
            "auto-report WiFi",
            INACTIVE_AUTOREPORT_WIFI_DEVICES_THRESHOLD_IN_SECONDS)

def _checkAndSendAlert(zoneManager, checkFunction, deviceTypeString, thresholdInSeconds):
    inactiveDevices = checkFunction(zm, thresholdInSeconds)

    if len(inactiveDevices) > 0:
        subject = "{} inactive {} devices".format(
                len(inactiveDevices), deviceTypeString)
        body = "The following devices haven't triggered "\
               "in the last {} hours\r\n  - ".format(
                       thresholdInSeconds / 3600)
        body += "\r\n  - ".join(inactiveDevices)

        alert = Alert.createInfoAlert(subject, body)
        if not AlertManager.processAdminAlert(alert):
            PE.logInfo('Failed to send inactive {} device alert'.format(deviceTypeString))
    else:
        PE.logInfo("No inactive {} devices detected.".format(deviceTypeString))

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

def getInactiveAutoReportWifiDevices(zoneManager, thresholdInSeconds):
    '''
    :rtype: list(str) the list of auto-reported WiFi devices that haven't
        sent anything in the specified number of seconds.
    '''
    inactiveDeviceName = []
    for z in zoneManager.getZones():
        autoReportDevices = [d for d in z.getDevices() if d.useWifi() and d.isAutoReport()]

        for d in autoReportDevices:
            if not d.wasRecentlyActivated(thresholdInSeconds):
                inactiveDeviceName.append(
                        "{}: {}".format(z.getName(), d.getItemName()))

    return inactiveDeviceName

#checkInactivity(scope.event)
#checkInactiveAutoReportWifiDevices(scope.event)
