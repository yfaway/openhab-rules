from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.types import UnDefType
from org.eclipse.smarthome.core.library.types import OnOffType

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
        :return: True if the state is ON.
        '''

        return OnOffType.ON == state

    @staticmethod
    def isInStateOff(state):
        '''
        :return: True if the state is OFF.
        '''

        return OnOffType.OFF == state

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
    def logInfo(message):
        ''' Log an info message. '''

        logger.info(message)
