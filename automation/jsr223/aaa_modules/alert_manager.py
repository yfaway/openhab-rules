import time
from org.slf4j import Logger, LoggerFactory
from openhab.actions import Mail

from aaa_modules import alert
reload(alert)
from aaa_modules.alert import *

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

_EMAIL_PROPERTIES_FILE = '/etc/openhab2/transform/owner-email-addresses.map'
_EMAIL_KEY = 'ALL_OWNER_EMAIL_ADDRESSES'

class AlertManager:
    # If set, the TTS message won't be sent to the chromecasts.
    _testMode = False

    # Used in unit testing to make sure that the email alert function was invoked,
    # without having to sent any actual email.
    _lastEmailedSubject = None

    # Tracks the timestamp of the last alert in a module.
    _moduleTimestamps = {}

    # Processes the provided alert.
    # If the alert's level is WARNING or CRITICAL, the TTS subject will be played
    # on the ChromeCasts.
    # @return True if alert was processed; False otherwise.
    # @throws ValueError if alert is None
    @staticmethod
    def processAlert(alert):
        if None == alert:
            raise ValueError('Invalid alert.')

        logger.info("Processing alert\n{}".format(alert.toString()))

        if None != alert.getModule():
            intervalInSeconds = alert.getIntervalBetweenAlertsInMinutes() * 60

            if alert.getModule() in AlertManager._moduleTimestamps:
                previousTime = AlertManager._moduleTimestamps[alert.getModule()]
                if (time.time() - previousTime) < intervalInSeconds:
                    return False

            AlertManager._moduleTimestamps[alert.getModule()] = time.time()

        AlertManager._emailAlert(alert)

        if alert.isWarningLevel() or alert.isCriticalLevel():
            cast_manager.playMessage(alert.getSubject())

        return True


    # Reset the internal states of this class.
    @staticmethod
    def reset():
        AlertManager._lastEmailedSubject = None
        AlertManager._moduleTimestamps = {}

    @staticmethod
    def _emailAlert(alert):
        emailAddresses = AlertManager._getEmailAddresses()
        if None == emailAddresses or len(emailAddresses) == 0:
            raise ValueError('Missing email addresses.')

        if not AlertManager._testMode:
            body = '' if alert.getBody() == None else alert.getBody()
            Mail.sendMail(';'.join(emailAddresses), alert.getSubject(),
                    alert.getBody(), alert.getAttachmentUrls())

        AlertManager._lastEmailedSubject = alert.getSubject()

    # @return list of email addresses
    @staticmethod
    def _getEmailAddresses():
        props = AlertManager._loadProperties(_EMAIL_PROPERTIES_FILE)
        emails = props[_EMAIL_KEY].split(';')

        return emails

    # @see https://stackoverflow.com/a/31852401
    @staticmethod
    def _loadProperties(filepath, sep='=', comment_char='#'):
	"""
	Read the file passed as parameter as a properties file.
	"""
	props = {}
	with open(filepath, "rt") as f:
	    for line in f:
		l = line.strip()
		if l and not l.startswith(comment_char):
		    key_value = l.split(sep)
		    key = key_value[0].strip()
		    value = sep.join(key_value[1:]).strip().strip('"') 
		    props[key] = value 
	return props

    # Switches on/off the test mode.
    # @param mode boolean
    @staticmethod
    def _setTestMode(mode):
        AlertManager._testMode = mode

