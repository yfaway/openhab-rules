class NeighborType:
    '''
    Define the various type of neighboring zones.
    '''

    UNDEFINED = -1
    '''
    Not specified or available.
    '''

    CLOSED_SPACE = 1
    '''
    The two zones are not connected.
    '''

    OPEN_SPACE = 2
    '''
    The two zones are treated as equal open space.
    '''

    OPEN_SPACE_MASTER = 3
    '''
    The two zones are open space, but this neighbor zone is considered to be
    more important.
    '''

    OPEN_SPACE_SLAVE = 4
    '''
    The two zones are open space, but this neighbor zone is considered to be
    less important.
    '''

class Neighbor:
    '''
    Represent a neighboring zone.
    '''

    def __init__(self, zoneId, type):
        '''
        Creates a new object

        :param str zoneId:
        :param NeighborType type:
        '''
        if None == zoneId or '' == zoneId:
            raise ValueError('zoneId must not be None or empty')

        if None == type:
            raise ValueError('type must not be None')

        self.zoneId = zoneId
        self.type = type

    def getZoneId(self):
        '''
        :rtype: str
        '''
        return self.zoneId

    def getType(self):
        '''
        :rtype: NeighborType
        '''
        return self.type

    def isOpenSpace(self):
        '''
        Returns True if the neighbor is not closed space.

        :rtype: boolean
        '''
        return NeighborType.OPEN_SPACE == self.getType() or \
                NeighborType.OPEN_SPACE_MASTER == self.getType() or \
                NeighborType.OPEN_SPACE_SLAVE == self.getType()
