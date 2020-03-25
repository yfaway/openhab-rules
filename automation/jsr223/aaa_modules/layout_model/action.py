class Action(object):

    '''
    The base class for all zone actions. An action is invoked when an event is
    triggered (e.g. when a motion sensor is turned on).
    
    An action may rely on the states of one or more sensors in the zone.
    '''

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return []

    def onAction(self, eventInfo):
        '''
        Subclass must override this method with its own handling.

        :param EventInfo eventInfo:
        :return: True if the event is processed; False otherwise.
        '''

        if not any(e == eventInfo.getEventType() for e in self.getTriggeringEvents()):
            return False
        
        return True
