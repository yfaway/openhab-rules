import json
from org.slf4j import Logger, LoggerFactory

LOG = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# The alert levels.
class Level:
    INFO = 1
    WARNING = 2
    CRITICAL = 3

# Contains information about the alert.
class Alert:
    # Creates an INFO alert.
    # @param subject string
    # @param body string, optional
    # @param attachmentUrls list of attachment URL strings
    # @param module string, optional
    # @param intervalBetweenAlertsInMinutes int, optional
    @classmethod
    def createInfoAlert(cls, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1):
        return cls(Level.INFO, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    # Creates an WARNING alert.
    # @param subject string
    # @param body string, optional
    # @param attachmentUrls list of attachment URL strings
    # @param module string, optional
    # @param intervalBetweenAlertsInMinutes int, optional
    @classmethod
    def createWarningAlert(cls, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1):
        return cls(Level.WARNING, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    # Creates an CRITICAL alert.
    # @param subject string
    # @param body string, optional
    # @param attachmentUrls list of attachment URL strings
    # @param module string, optional
    # @param intervalBetweenAlertsInMinutes int, optional
    @classmethod
    def createCriticalAlert(cls, subject, body = None, attachmentUrls = [],
            module = None, intervalBetweenAlertsInMinutes = -1):
        return cls(Level.CRITICAL, subject, body, attachmentUrls, module,
                intervalBetweenAlertsInMinutes)

    # Creates a new object from information in the json string. This method
    # is used for alerts coming in from outside the jsr223 framework; they 
    # will be in JSON format.
    # Accepted keys: subject, body, level ('info', 'warning', or 'critical').
    # @param jsonString string
    # @throw ValueError if jsonString contains invalid values
    @classmethod
    def fromJson(cls, jsonString):
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
        return self.subject

    def getBody(self):
        return self.body

    def getAttachmentUrls(self):
        return self.attachmentUrls

    # Returns the alert module
    # @return string
    def getModule(self):
        return self.module

    # Returns the overriding email addresses to be used instead of the default
    # email addresses.
    # @return string or None if not specified
    def getEmailAddresses(self):
        return self.emailAddresses

    # @return int
    def getIntervalBetweenAlertsInMinutes(self):
        return self.intervalBetweenAlertsInMinutes

    def isInfoLevel(self):
        return Level.INFO == self.level

    def isWarningLevel(self):
        return Level.WARNING == self.level

    def isCriticalLevel(self):
        return Level.CRITICAL == self.level

    # Returns a user readable string containing this object's info.
    def toString(self):
        returnedVal = ''
        if self.isInfoLevel():
            returnedVal += '[INFO]'
        elif self.isWarningLevel():
            returnedVal += '[WARNING]'
        else:
            returnedVal += '[CRITICAL]'

        returnedVal += ' {}\n{}\n{}'.format(self.getSubject(), self.getBody(), 
                str(self.getAttachmentUrls()))

        return returnedVal
