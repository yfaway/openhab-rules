''' A mocked ZoneManager used during unit testing.'''

class MockedZoneManager:
    def __init__(self, zones):
        self.zones = zones

    def getZoneById(self, id):
        for z in self.zones:
            if z.getId() == id:
                return z

        return None

    def getDevicesByType(self, cls):
        return []
