import time
from core.jsr223.scope import actions

from aaa_modules.alert import *
from aaa_modules import cast_manager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.devices.activity_times import ActivityTimes

_EMAIL_PROPERTIES_FILE = '/etc/openhab2/transform/owner-email-addresses.map'
_ADMIN_EMAIL_KEY = 'admin-email-address'
_OWNER_EMAIL_KEY = 'owner-email-address'

class AlertManager:
    '''
    Process an alert.
    The current implementation will send out an email. If the alert is at
    critical level, a TTS message will also be sent to all audio sinks.
    '''

    _testMode = False
    '''
    If set, the TTS message won't be sent to the chromecasts.
    '''

    _lastEmailedSubject = None
    '''
    Used in unit testing to make sure that the email alert function was invoked,
    without having to sent any actual email.
    '''

    _moduleTimestamps = {}
    '''
    Tracks the timestamp of the last alert in a module.
    '''

    @staticmethod
    def processAlert(alert, zoneManager = None):
        '''
        Processes the provided alert.
        If the alert's level is WARNING or CRITICAL, the TTS subject will be played
        on the ChromeCasts.

        :param Alert alert: the alert to be processed
        :param ImmutableZoneManager zoneManager: used to retrieve the ActivityTimes
        :return: True if alert was processed; False otherwise.
        :raise: ValueError if alert is None
        '''

        if None == alert:
            raise ValueError('Invalid alert.')

        PE.logInfo(u"Processing alert\n{}".format(alert.toString()))

        if AlertManager._isThrottled(alert):
            return False

        if not alert.isAudioAlertOnly():
            AlertManager._emailAlert(
                    alert, AlertManager._getOwnerEmailAddresses())

        # Play an audio message if the alert is warning or critical.
        # Determine the volume based on the current zone activity.
        volume = 0
        if alert.isCriticalLevel():
            volume = 60
        elif alert.isWarningLevel():
            if None == zoneManager:
                volume = 60
            else:
                activity = zoneManager.getDevicesByType(ActivityTimes)[0]
                if activity.isSleepTime():
                    volume = 0
                elif activity.isQuietTime():
                    volume = 40
                else:
                    volume = 60

        if volume > 0:
            casts = cast_manager.getAllCasts()
            cast_manager.playMessage(alert.getSubject(), casts, volume)

        return True

    @staticmethod
    def processAdminAlert(alert):
        '''
        Processes the provided alert by sending an email to the administrator.

        :param Alert alert: the alert to be processed
        :return: True if alert was processed; False otherwise.
        :raise: ValueError if alert is None
        '''

        if None == alert:
            raise ValueError('Invalid alert.')

        PE.logInfo(u"Processing admin alert\n{}".format(alert.toString()))

        if AlertManager._isThrottled(alert):
            return False

        AlertManager._emailAlert(
                alert, AlertManager._getAdminEmailAddresses())

        return True

    @staticmethod
    def reset():
        '''
        Reset the internal states of this class.
        '''
        AlertManager._lastEmailedSubject = None
        AlertManager._moduleTimestamps = {}

    @staticmethod
    def _isThrottled(alert):
        if None != alert.getModule():
            intervalInSeconds = alert.getIntervalBetweenAlertsInMinutes() * 60

            if alert.getModule() in AlertManager._moduleTimestamps:
                previousTime = AlertManager._moduleTimestamps[alert.getModule()]
                if (time.time() - previousTime) < intervalInSeconds:
                    return True

            AlertManager._moduleTimestamps[alert.getModule()] = time.time()

        return False

    @staticmethod
    def _emailAlert(alert, defaultEmailAddresses):
        emailAddresses = alert.getEmailAddresses()
        if [] == emailAddresses:
            emailAddresses = defaultEmailAddresses

        if None == emailAddresses or len(emailAddresses) == 0:
            raise ValueError('Missing email addresses.')

        if not AlertManager._testMode:
            body = '' if alert.getBody() == None else alert.getBody()
            actions.get("mail", "mail:smtp:gmail").sendMail(
                    ', '.join(emailAddresses),
                    alert.getSubject(),
                    alert.getBody(),
                    alert.getAttachmentUrls())

        AlertManager._lastEmailedSubject = alert.getSubject()

    @staticmethod
    def _getAdminEmailAddresses():
        '''
        :return: list of administrator email addresses
        '''
        props = AlertManager._loadProperties(_EMAIL_PROPERTIES_FILE)
        emails = props[_ADMIN_EMAIL_KEY].split(';')

        return emails

    @staticmethod
    def _getOwnerEmailAddresses():
        '''
        :return: list of user email addresses
        '''
        props = AlertManager._loadProperties(_EMAIL_PROPERTIES_FILE)
        emails = props[_OWNER_EMAIL_KEY].split(';')

        return emails

    @staticmethod
    def _loadProperties(filepath, sep='=', comment_char='#'):
	"""
	Read the file passed as parameter as a properties file.
        @see https://stackoverflow.com/a/31852401
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

    @staticmethod
    def _setTestMode(mode):
        '''
        Switches on/off the test mode.
        @param mode boolean
        '''
        AlertManager._testMode = mode

