from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.types import UnDefType
from org.eclipse.smarthome.core.library.types import OnOffType
from org.eclipse.smarthome.core.library.types import OpenClosedType

from core.testing import run_test

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

class PlatformEncapsulator:
    '''
    Abstract away the OpenHab classes.
    '''

    @staticmethod
    def isStateAvailable(state):
        '''
        :return: True if the state is not of type UndefType.
        '''

        return not isinstance(state, UnDefType)

    @staticmethod
    def isInStateOn(state):
        '''
        :param org.eclipse.smarthome.core.types.State state:
        :return: True if the state is ON.
        '''

        return OnOffType.ON == state

    @staticmethod
    def isInStateOff(state):
        '''
        :param org.eclipse.smarthome.core.types.State state:
        :return: True if the state is OFF.
        '''

        return OnOffType.OFF == state

    @staticmethod
    def isInStateOpen(state):
        '''
        :param org.eclipse.smarthome.core.types.State state:
        :return: True if the state is OPEN.
        '''

        return OpenClosedType.OPEN == state

    @staticmethod
    def isInStateClosed(state):
        '''
        :param org.eclipse.smarthome.core.types.State state:
        :return: True if the state is CLOSED.
        '''

        return OpenClosedType.CLOSED == state

    @staticmethod
    def getIntegerStateValue(item, defaultVal):
        '''
        :param openHabItem item: 
        :param * defaultVal: the value to return if the state is not available 
        :return: the integer state value or defaultVal is the state is not
            available.
        :rtype: int
        '''

        if PlatformEncapsulator.isStateAvailable(item.getState()):
            return item.getState().intValue()
        else:
            return defaultVal

    @staticmethod
    def getLogger():
        '''
        Returns the logger.

        :rtype: Logger
        '''
        return logger

    @staticmethod
    def logInfo(message):
        ''' Log an info message. '''

        logger.info(message)

    @staticmethod
    def logWarning(message):
        ''' Log an warning message. '''

        logger.warn(message)

    @staticmethod
    def logError(message):
        ''' Log an error message. '''

        logger.error(message)

    @staticmethod
    def runUnitTest(className):
        ''' Run the unit test. '''
        run_test(className, logger) 
