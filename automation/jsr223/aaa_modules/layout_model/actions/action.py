# The base class for all zone actions. An action is invoked when an event is
# triggered (e.g. when a motion sensor is turned on).
# An action may rely on the states of one or more sensors in the zone.
class Action(object):

    # Subclass must override this method with its own handling.
    # @param events scope.events
    # @param zone Zone the zone where the action takes place
    # @param getZoneByIdFn lambda a function that returns a Zone object given
    #     a zone id string
    # @return True if the event is processed; False otherwise.
    def onAction(self, events, zone, getZoneByIdFn):
        pass
