'''
Contain utility methods and constants dealing with the house's security sytem.
'''

from org.eclipse.smarthome.core.library.types import OnOffType

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
    return items['VT_In_Vacation'] == OnOffType.ON
