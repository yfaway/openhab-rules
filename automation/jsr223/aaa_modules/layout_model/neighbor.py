# Define the various type of neighboring zones.
class NeighborType:
    # Not specified or available.
    UNDEFINED = -1

    CLOSED_SPACE = 1

    # The two zones are treated as equal open space.
    OPEN_SPACE = 2

    # The two zones are open space, but this neighbor zone is considered to be
    # more important.
    OPEN_SPACE_MASTER = 3

    # The two zones are open space, but this neighbor zone is considered to be
    # less important.
    OPEN_SPACE_SLAVE = 4

class Neighbor:
    # Creates a new object
    # @param zone Zone
    # @param type NeighborType
    def __init__(self, zone, type):
        if None == zone:
            raise ValueError('zone must not be None')

        if None == type:
            raise ValueError('type must not be None')

        self.zone = zone
        self.type = type

    def getZone(self):
        return self.zone

    def getType(self):
        return self.type
