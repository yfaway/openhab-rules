# This file processes legacy Xtend alert messages sent through the
# VT_AlertSender string item.
from org.slf4j import Logger, LoggerFactory
from openhab.rules import rule
from openhab.triggers import when

from aaa_modules import alert_manager
reload(alert_manager)
from aaa_modules.alert_manager import *

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

_ALERT_ITEM_NAME = 'VT_AlertSender'

@rule("Send alert")
@when("Item {} received update".format(_ALERT_ITEM_NAME))
def sendAlert(event):
    json = items[_ALERT_ITEM_NAME].toString()
    alert = Alert.fromJson(json)

    if AlertManager.processAlert(alert):
        return True
    else:
        logger.error('Failed to send alert {}' % alert.toString())
        return False

