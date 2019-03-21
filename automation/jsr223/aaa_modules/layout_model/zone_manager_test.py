import unittest

from core.jsr223 import scope
from core.testing import run_test
from org.slf4j import Logger, LoggerFactory
from org.eclipse.smarthome.core.library.items import SwitchItem

from aaa_modules.layout_model import zone_manager
reload(zone_manager)
from aaa_modules.layout_model.zone_manager import ZoneManager

from aaa_modules.layout_model import zone
reload(zone)
from aaa_modules.layout_model.zone import Zone

from aaa_modules.layout_model import switch
reload(switch)
from aaa_modules.layout_model.switch import Light

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

LIGHT_SWITCH_NAME = 'TestLightName'
TIMER_NAME = 'TestTimerName'

# Unit tests for zone_manager.py.
class ZoneManagerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        ZoneManager.removeAllZones()

    def testAddZone_validZone_zoneAdded(self):
        zone1 = Zone('ff')
        ZoneManager.addZone(zone1)
        self.assertEqual(1, len(ZoneManager.getZones()))

        zone2 = Zone('2f')
        ZoneManager.addZone(zone2)
        self.assertEqual(2, len(ZoneManager.getZones()))

    def testRemoveZone_validZone_zoneRemoved(self):
        zone1 = Zone('ff')
        ZoneManager.addZone(zone1)

        zone2 = Zone('2f')
        ZoneManager.addZone(zone2)

        self.assertEqual(2, len(ZoneManager.getZones()))

        ZoneManager.removeZone(zone1)
        self.assertEqual(1, len(ZoneManager.getZones()))

        ZoneManager.removeZone(zone2)
        self.assertEqual(0, len(ZoneManager.getZones()))

run_test(ZoneManagerTest, logger) 
