class Action(object):
    '''
    The base class for all zone actions. An action is invoked when an event is
    triggered (e.g. when a motion sensor is turned on).
    
    An action may rely on the states of one or more sensors in the zone.
    '''

    def onAction(self, events, zone, getZoneByIdFn):
        '''
        Subclass must override this method with its own handling.

        :param scope.events events:
        :param Zone zone: the zone where the action takes place
        :param lambda getZoneByIdFn: a function that returns a Zone object given\
        a zone id string
        :return: True if the event is processed; False otherwise.
        '''
        pass
