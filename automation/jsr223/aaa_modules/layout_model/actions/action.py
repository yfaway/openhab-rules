class Action(object):
    '''
    The base class for all zone actions. An action is invoked when an event is
    triggered (e.g. when a motion sensor is turned on).
    
    An action may rely on the states of one or more sensors in the zone.
    '''

    def onAction(self, events, zone, zoneManager):
        '''
        Subclass must override this method with its own handling.

        :param scope.events events:
        :param Zone zone: the zone where the action takes place
        :param ImmutableZoneManager zoneManager: contains all available zones \
            as well as useful general functions.
        :return: True if the event is processed; False otherwise.
        '''
        pass
