# The vertical levels.
class Level:
    UNDEFINED = 0
    FIRST_FLOOR = 1
    SECOND_FLOOR = 2
    THIRD_FLOOR = 3
    BASEMENT = 4

# Represent a zone such as a room, foyer, porch, or lobby.
class Zone:
    def __init__(self, name, devices = [], level = Level.UNDEFINED):
        self.name = name
        self.level = level
        this.devices = devices

    def addDevice(self, device):
        self.devices.add(device)

    def removeDevice(self, device):
        self.devices.remove(device)

    def getDevices(self):
        return [d for d in self.devices]

    def getDevicesByType(self, cls):
        return [d for d in self.devices if isinstance(d, cls)]

    def getName(self):
        return self.name

    def getLevel(self):
        return self.level

