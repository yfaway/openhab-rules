from aaa_modules.layout_model.device import Device
from org.eclipse.smarthome.core.library.types import OnOffType

class AlarmPartition(Device):
    '''
    Represents a security control. Exposes methods to arm the security system,
    and provide the alarm status.

    The current implementatio is for DSC Alarm system.
    '''

    STATE_UNARMED = 0
    ''' The value for the unarmed state.  '''

    STATE_ARM_AWAY = 1
    ''' The value for the arm away state.  '''

    STATE_ARM_STAY = 2
    ''' The value for the arm stay state.  '''

    def __init__(self, alarmStatusItem, armModeItem):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.SwitchItem alarmStatusItem: \
            the item to indicate if the system is in alarm
        :param org.eclipse.smarthome.core.library.items.NumberItem armModeItem: \
            the item to set the arming/disarming mode
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, alarmStatusItem)

        if None == armModeItem:
            raise ValueError('armModeItem must not be None')

        self.armModeItem = armModeItem

    def isInAlarm(self):
        '''
        :return: True if the partition is in alarm; False otherwise
        :rtype: bool
        '''
        return OnOffType.ON == self.getItem().getState()

    def getArmMode(self):
        '''
        :return: one of STATE_UNARMED, STATE_ARM_AWAY, STATE_ARM_STAY
        :rtype: int
        '''
        return self.armModeItem.getState().intValue()

    def armAway(self, events):
        '''
        Arm-away the partiton.

        :param scope.events events:
        '''
        events.sendCommand(self.armModeItem, AlarmPartition.STATE_ARM_AWAY)

    def armStay(self, events):
        '''
        Arm-stay the partiton.

        :param scope.events events:
        '''
        events.sendCommand(self.armModeItem, AlarmPartition.STATE_ARM_STAY)

    def disarm(self, events):
        '''
        Disarm the partiton.

        :param scope.events events:
        '''
        events.sendCommand(self.armModeItem, AlarmPartition.STATE_UNARMED)

