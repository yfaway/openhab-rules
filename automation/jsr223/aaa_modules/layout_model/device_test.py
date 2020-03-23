import abc
import unittest

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import DimmerItem
from org.eclipse.smarthome.core.library.items import NumberItem
from org.eclipse.smarthome.core.library.types import DecimalType
from org.eclipse.smarthome.core.library.types import OnOffType
from org.eclipse.smarthome.core.library.types import PercentType

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

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

    def getMockedEventDispatcher(self):
        return MockedEventDispatcher(scope.itemRegistry)


class MockedEventDispatcher:
    """
    Mocked the scope.events object to directly change the state of the item
    instead of going through the event bus. This reduces the wait time, and 
    more importantly, makes sendCommand synchronous (no need to inject
    time.sleep() to wait for the command to finish).

    The itemRegistry needs to be passed in, as it is not retrievable from
    'scope' if the current thread is not the main thread.
    """

    def __init__(self, itemRegistry):
        self.itemRegistry = itemRegistry

    def sendCommand(self, itemName, command):
        item = self.itemRegistry.getItem(itemName)

        if command == "ON":
            item.setState(OnOffType.ON)
        elif command == "OFF":
            item.setState(OnOffType.OFF)
        elif isinstance(item, DimmerItem):
            item.setState(PercentType(command))
        elif isinstance(item, NumberItem):
            item.setState(DecimalType(command))
        else:
            raise ValueError("Unsupported command value '{}'".format(command))
