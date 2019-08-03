import json
from org.slf4j import Logger, LoggerFactory

LOG = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class Level:
    '''
    The alert levels.
    '''

    INFO = 1
    ''' INFO '''

    WARNING = 2
    ''' WARNING '''

    CRITICAL = 3
    ''' CRITICAL '''

class Alert:
    '''
    Contains information about the alert.
    '''

    @classmethod
    def createInfoAlert(cls, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1):
        '''
        Creates an INFO alert.

        :param string subject:
        :param list(str) attachmentUrls: list of URL attachment strings:
        :param string module: (optional)
        :param int intervalBetweenAlertsInMinutes: (optional)
        '''
        return cls(Level.INFO, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    @classmethod
    def createWarningAlert(cls, subject, body = None, attachmentUrls = [],
           module = None, intervalBetweenAlertsInMinutes = -1):
        '''
        Creates a WARNING alert.

        :param string subject:
        :param list(str) attachmentUrls: list of URL attachment strings:
        :param string module: (optional)
        :param int intervalBetweenAlertsInMinutes: (optional)
        '''
        return cls(Level.WARNING, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    @classmethod
    def createCriticalAlert(cls, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1):
        '''
        Creates a CRITICAL alert.

        :param string subject:
        :param list(str) attachmentUrls: list of URL attachment strings:
        :param string module: (optional)
        :param int intervalBetweenAlertsInMinutes: (optional)
        '''
        return cls(Level.CRITICAL, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    @classmethod
    def fromJson(cls, jsonString):
        '''
        Creates a new object from information in the json string. This method
        is used for alerts coming in from outside the jsr223 framework; they 
        will be in JSON format.
        Accepted keys: subject, body, level ('info', 'warning', or 'critical').

        :param str jsonString:
        :raise: ValueError if jsonString contains invalid values
        '''

        # set strict to false to allow control characters in the json string
        obj = json.loads(jsonString, strict=False)

        subject = obj.get('subject', None)
        if None == subject or '' == subject:
            raise ValueError('Missing subject value.')

        body = obj.get('body', None)

        levelMappings = {
            'info': Level.INFO,
            'warning': Level.WARNING,
            'critical': Level.CRITICAL
        }
        level = Level.INFO
        if 'level' in obj:
            level = levelMappings.get(obj['level'], None)

        if None == level:
            raise ValueError('Invalid alert level.')

        module = obj.get('module', None)
        if '' == module:
            module = None

        intervalBetweenAlertsInMinutes = obj.get(
                'intervalBetweenAlertsInMinutes', -1)
        if None != module and intervalBetweenAlertsInMinutes <= 0:
            raise ValueError('Invalid intervalBetweenAlertsInMinutes value: ' 
                    + str(intervalBetweenAlertsInMinutes))

        attachmentUrls = []

        emailAddresses = obj.get('emailAddresses', None)
        return cls(level, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes, emailAddresses)

    def __init__(self, level, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1,
            emailAddresses = None):
        self.level = level
        self.subject = subject
        self.body = body
        self.attachmentUrls = attachmentUrls
        self.module = module
        self.intervalBetweenAlertsInMinutes = intervalBetweenAlertsInMinutes
        self.emailAddresses = emailAddresses

    def getSubject(self):
        '''
        :rtype: str
        '''
        return self.subject

    def getBody(self):
        '''
        :rtype: str
        '''
        return self.body

    def getAttachmentUrls(self):
        '''
        :rtype: list(str)
        '''
        return self.attachmentUrls

    def getModule(self):
        '''
        Returns the alert module

        :rtype: str
        '''
        return self.module

    def getEmailAddresses(self):
        '''
        Returns the overriding email addresses to be used instead of the default
        email addresses.

        :return: a list of email addresses; empty list if not specified
        :rtype: list(str)
        '''

        return [] if None == self.emailAddresses else self.emailAddresses.split(';')

    def getIntervalBetweenAlertsInMinutes(self):
        '''
        :rtype: int
        '''
        return self.intervalBetweenAlertsInMinutes

    def isInfoLevel(self):
        '''
        :rtype: bool
        '''
        return Level.INFO == self.level

    def isWarningLevel(self):
        '''
        :rtype: bool
        '''
        return Level.WARNING == self.level

    def isCriticalLevel(self):
        '''
        :rtype: bool
        '''
        return Level.CRITICAL == self.level

    def toString(self):
        '''
        :return: a user readable string containing this object's info.
        '''
        returnedVal = u''
        if self.isInfoLevel():
            returnedVal += '[INFO]'
        elif self.isWarningLevel():
            returnedVal += '[WARNING]'
        else:
            returnedVal += '[CRITICAL]'

        returnedVal += u' {}\n{}\n{}'.format(self.getSubject(), self.getBody(), 
                str(self.getAttachmentUrls()))

        return returnedVal
