from org.slf4j import Logger, LoggerFactory

from aaa_modules import alert
reload(alert)
from aaa_modules.alert import *

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Processes the provided alert.
# If the alert's level is WARNING or CRITICAL, the TTS subject will be played
# on the ChromeCasts.
def processAlert(alert):
    if None == alert:
        raise ValueError('Invalid alert.')

    logger.info("Processing alert '{}'".format(alert.getSubject()))

    if alert.isWarningLevel() or alert.isCriticalLevel():
        cast_manager.playMessage(alert.getSubject())
