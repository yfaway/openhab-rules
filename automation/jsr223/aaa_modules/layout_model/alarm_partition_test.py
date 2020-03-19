import time

from core.jsr223 import scope
from org.eclipse.smarthome.core.library.items import SwitchItem, NumberItem
from org.eclipse.smarthome.core.library.types import DecimalType

from aaa_modules.layout_model.device_test import DeviceTest

#from aaa_modules.layout_model import alarm_partition
#reload(alarm_partition)
from aaa_modules.layout_model.alarm_partition import AlarmPartition
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

ITEMS = [SwitchItem('_AlarmStatus'), NumberItem('_AlarmMode')]

# Unit tests for alarm_partition.py.
class AlarmPartitionTest(DeviceTest):

    def setUp(self):
        super(AlarmPartitionTest, self).setUp()
        self.alarmPartition = AlarmPartition(self.getItems()[0],
            self.getItems()[1])

    def getItems(self, resetState = False):
        if resetState:
            ITEMS[0].setState(scope.OnOffType.OFF)
            ITEMS[1].setState(DecimalType(AlarmPartition.STATE_UNARMED))

        return ITEMS

    def testIsInAlarm_notInAlarm_returnsFalse(self):
        self.assertFalse(self.alarmPartition.isInAlarm())

    def testIsInAlarm_inAlarm_returnsTrue(self):
        ITEMS[0].setState(scope.OnOffType.ON)
        self.assertTrue(self.alarmPartition.isInAlarm())

    def testArmAway_noParam_setCorrectValue(self):
        self.alarmPartition.armAway(scope.events)

        time.sleep(0.1)
        self.assertEqual(AlarmPartition.STATE_ARM_AWAY,
                self.alarmPartition.getArmMode())

    def testArmStay_noParam_setCorrectValue(self):
        self.alarmPartition.armStay(scope.events)

        time.sleep(0.1)
        self.assertEqual(AlarmPartition.STATE_ARM_STAY,
                self.alarmPartition.getArmMode())

    def testDisarm_noParam_setCorrectValue(self):
        self.alarmPartition.disarm(scope.events)

        time.sleep(0.1)
        self.assertEqual(AlarmPartition.STATE_UNARMED,
                self.alarmPartition.getArmMode())

PE.runUnitTest(AlarmPartitionTest)
