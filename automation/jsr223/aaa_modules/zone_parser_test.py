import unittest

from core.jsr223 import scope

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.alarm_partition import AlarmPartition
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.dimmer import Dimmer
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Light, Fan

#from aaa_modules import zone_parser
#reload(zone_parser)
from aaa_modules.zone_parser import ZoneParser

# Unit tests for zone_parser.py.
class ZoneParserTest(unittest.TestCase):

    def testParse_scopeHasItems_returnsNonEmptyZoneList(self):
        zones = ZoneParser.parse(scope.items, scope.itemRegistry)
        self.assertTrue(len(zones) > 0)

        for z in zones:
            self.assertTrue(len(z.getDevices()) > 0)

        self.assertTrue(any(len(z.getDevicesByType(AstroSensor)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(Dimmer)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(Fan)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(IlluminanceSensor)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(Light)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(MotionSensor)) > 0 for z in zones))
        self.assertTrue(any(len(z.getDevicesByType(AlarmPartition)) > 0 for z in zones))

PE.runUnitTest(ZoneParserTest)
