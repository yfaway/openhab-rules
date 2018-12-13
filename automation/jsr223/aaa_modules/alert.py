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
    # @param level int a value in Level class
    # @param subject string
    # @param body string, optional
    @classmethod
    def createSimpleAlert(cls, level, subject, body = None):
        return cls(level, subject, body)

    # Creates a new object from information in the json string.
    # Accepted keys: subject, body, level ('info', 'warning', or 'critical').
    # @param jsonString string
    # @throw ValueError if jsonString contains invalid values
    @classmethod
    def fromJson(cls, jsonString):
        obj = json.loads(jsonString)

        subject = obj['subject']
        body = None if not 'body' in obj else obj['body']

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

        return cls(level, subject, body)

    def __init__(self, level, subject, body):
        self.level = level
        self.subject = subject
        self.body = body

    def getSubject(self):
        return self.subject

    def getBody(self):
        return self.body

    def isInfoLevel(self):
        return Level.INFO == self.level

    def isWarningLevel(self):
        return Level.WARNING == self.level

    def isCriticalLevel(self):
        return Level.CRITICAL == self.level
