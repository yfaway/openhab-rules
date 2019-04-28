# The base class for all zone actions. An action is invoked when an event is
# triggered (e.g. when a motion sensor is turned on).
# An action may rely on the states of one or more sensors in the zone.
class Action(object):

    # Subclass must override this method with its own handling.
    # @param events scope.events
    # @param zone Zone
    # @return True if the event is processed; False otherwise.
    def onAction(self, events, zone):
        pass
