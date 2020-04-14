'''
Contain utility methods and constants dealing with the house's security sytem.
'''
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition

ITEM_NAME_PARTITION_ARM_MODE = "PARTITION1_ARM_MODE"
''' The item name for the partition arm mode.  '''

STATE_UNARMED = 0
''' The value for the unarmed state.  '''

STATE_ARM_AWAY = 1
''' The value for the arm away state.  '''

STATE_ARM_STAY = 2
''' The value for the arm stay state.  '''

WHEN_CHANGED_TO_ARMED_AWAY = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_AWAY)
''' The @when condition when system is armed away.  '''

WHEN_CHANGED_TO_ARMED_STAY = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_STAY)
''' The @when condition when system is armed stay.  '''

WHEN_CHANGED_TO_UNARMED = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_UNARMED)
''' The @when condition when system is unarmed.  '''

WHEN_CHANGED_FROM_ARM_AWAY_TO_UNARMED = "Item {0} changed from {1:d} to {2:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_AWAY, STATE_UNARMED)
''' The @when condition when system is changed from armed away to unarmed.  '''


def isInVacation(items):
    '''
    :param scope.items items:
    :return: True if the house is set to vacation mode.
    '''
    return PE.isInStateOn(items['VT_In_Vacation'])


class SecurityManager:
    '''
    Provide quick access to the alarm partition of the zones.
    '''

    @staticmethod
    def isArmedAway(zoneManager):
        '''
        :return: True if at least one zone is armed-away
        '''
        securityPartitions = zoneManager.getDevicesByType(AlarmPartition)
        if len(securityPartitions) > 0:
            if AlarmPartition.STATE_ARM_AWAY == securityPartitions[0].getArmMode():
                return True

        return False

    @staticmethod
    def isArmedStay(zoneManager):
        '''
        :return: True if at least one zone is armed-stay
        '''
        securityPartitions = zoneManager.getDevicesByType(AlarmPartition)
        if len(securityPartitions) > 0:
            if AlarmPartition.STATE_ARM_STAY == securityPartitions[0].getArmMode():
                return True

        return False
