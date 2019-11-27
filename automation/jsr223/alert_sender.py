# This file processes legacy Xtend alert messages sent through the
# VT_AlertSender string item.
from core.rules import rule
from core.triggers import when

from aaa_modules.alert_manager import *
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

_ALERT_ITEM_NAME = 'VT_AlertSender'

@rule("Send alert")
@when("Item {} received update".format(_ALERT_ITEM_NAME))
def sendAlert(event):
    json = items[_ALERT_ITEM_NAME].toString()
    alert = Alert.fromJson(json)

    if AlertManager.processAlert(alert):
        return True
    else:
        PE.logError('Failed to send alert {}'.format(alert.toString()))
        return False

