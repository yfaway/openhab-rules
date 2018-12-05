# Contain utility methods and constants dealing with the house's security sytem.

ITEM_NAME_PARTITION_ARM_MODE = "PARTITION1_ARM_MODE"
STATE_ARM_AWAY = 1

# The @when condition when system is armed away.
WHEN_CHANGED_TO_ARMED_AWAY = "Item {0} changed to {1:d}".format(
        ITEM_NAME_PARTITION_ARM_MODE, STATE_ARM_AWAY)
