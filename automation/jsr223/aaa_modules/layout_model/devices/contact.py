from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class Contact(Device):
    '''
    Represents a contact such as a door or windows.
    '''

    def __init__(self, contactItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.SwitchItem contactItem:
        :raise ValueError: if any parameter is invalid
        '''

        Device.__init__(self, contactItem)

    def isOpen(self):
        '''
        Returns true if the contact is open; false otherwise.
        '''
        return PE.isInStateOpen(self.getItem().getState()) \
            or PE.isInStateOn(self.getItem().getState())

    def isClosed(self):
        '''
        Returns true if the contact is closed; false otherwise.
        '''
        return not self.isOpen()

class Door(Contact):
    '''
    Represents a door.
    '''
    pass

class Window(Contact):
    '''
    Represents a window.
    '''
    pass
