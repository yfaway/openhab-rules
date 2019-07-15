# Contain utility methods and constants dealing with the house's security sytem.

from org.eclipse.smarthome.core.library.types import OnOffType

ITEM_NAME_PARTITION_ARM_MODE = "PARTITION1_ARM_MODE"
STATE_UNARMED = 0
STATE_ARM_AWAY = 1
STATE_ARM_STAY = 2

# The @when condition when system is armed away.
WHEN_CHANGED_TO_ARMED_AWAY = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_AWAY)

WHEN_CHANGED_TO_ARMED_STAY = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_STAY)

WHEN_CHANGED_TO_UNARMED = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_UNARMED)

WHEN_CHANGED_FROM_ARM_AWAY_TO_UNARMED = "Item {0} changed from {1:d} to {2:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_AWAY, STATE_UNARMED)

# Returns True if the house is set to vacation mode.
# @param items scope.items
def isInVacation(items):
    return items['VT_In_Vacation'] == OnOffType.ON
