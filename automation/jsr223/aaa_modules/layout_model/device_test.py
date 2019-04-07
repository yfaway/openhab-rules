import abc
import unittest

from core.jsr223 import scope

# Base test class for Device derived sensors.
class DeviceTest(unittest.TestCase):
    # Returns a list of items to register. 
    # @param resetState if set, reset the state of the item
    @abc.abstractmethod
    def getItems(self, resetState = False):
        "abstract method"

    # Adds the items to the registry.
    def setUp(self):
        for item in self.getItems(True):
            scope.itemRegistry.remove(item.getName())
            scope.itemRegistry.add(item)

    # Removes the items from the registry.
    def tearDown(self):
        for item in self.getItems(True):
            scope.itemRegistry.remove(item.getName())

