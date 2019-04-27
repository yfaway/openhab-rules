import re

from core import osgi
from core.jsr223 import scope
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.slf4j import Logger, LoggerFactory

from aaa_modules.layout_model.zone import Zone, Level
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.dimmer import Dimmer
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Fan, Light

META_DIMMING_SETTING = 'dimmable'

# The light level threshold; if it is below this value, turn on the light.
ILLUMINANCE_THRESHOLD_IN_LUX = 8

TIME_OF_DAY_ITEM_NAME = 'VT_Time_Of_Day'

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")
logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Construct the zones from the existing items in OpenHab, using this naming
# convention: Floor_Location_ItemType
# For example, item "Switch FF_Foyer_LightSwitch ..." will create a zone named
# 'Foyer' at the first floor; and the zone contains a Light object.
class ZoneParser:
    # @param items scope.items
    # @param itemRegistry scope.itemRegistry
    # @return a list of aaa_modules.layout_model.zone.Zone objects
    @staticmethod
    def parse(items, itemRegistry):
        zoneMap = {}
        keyPattern = '([^_]+)_([^_]+)_(.+)' # level_location_deviceName

        for itemName in items.keys():
            match = re.search('([^_]+)_([^_]+)_(.+)', itemName)
            if not match:
                continue

            levelString = match.group(1)
            location = match.group(2)
            deviceName = match.group(3)
            
            zoneKey = levelString + '_' + location
            if zoneKey in zoneMap:
                zone = zoneMap[zoneKey]
            else:
                zone = Zone(location, [], ZoneParser.getZoneLevel(levelString))

            openHabItem = itemRegistry.getItem(itemName)
            if 'LightSwitch' == deviceName:
                timerItem = itemRegistry.getItem(itemName + '_Timer')

                meta = MetadataRegistry.get(
                        MetadataKey(META_DIMMING_SETTING, itemName)) 
                if None != meta:
                    config = meta.configuration
                    level = config['level'].intValue()
                    timeRanges = config['timeRanges']

                    switch = Dimmer(openHabItem, timerItem, level, timeRanges,
                            ILLUMINANCE_THRESHOLD_IN_LUX)
                else:
                    switch = Light(openHabItem, timerItem, ILLUMINANCE_THRESHOLD_IN_LUX)

                zone.addDevice(switch)
            elif 'FanSwitch' == deviceName:
                fan = Fan(openHabItem,
                        itemRegistry.getItem(itemName + '_Timer'))
                zone.addDevice(fan)
            elif 'LightSwitch_Illuminance' == deviceName:
                illuminanceSensor = IlluminanceSensor(openHabItem)
                zone.addDevice(illuminanceSensor)
            elif deviceName.endswith('MotionSensor'):
                motionSensor = MotionSensor(openHabItem)
                zone.addDevice(motionSensor)

            if len(zone.getDevices()) > 0:
                zoneMap[zoneKey] = zone

            # end looping items

        astroSensor = AstroSensor(itemRegistry.getItem(TIME_OF_DAY_ITEM_NAME))
        for z in zoneMap.values():
            if len(z.getDevicesByType(Light)) > 0 or \
                    len(z.getDevicesByType(Dimmer)) > 0:
                z.addDevice(astroSensor)

        return zoneMap.values()
                

    # @return aaa_modules.layout_model.zone.Level 
    @staticmethod
    def getZoneLevel(levelString):
        if 'BM' == levelString:
            return Level.BASEMENT
        elif 'FF' == levelString:
            return Level.FIRST_FLOOR
        elif 'SF' == levelString:
            return Level.SECOND_FLOOR
        elif 'TF' == levelString:
            return Level.THIRD_FLOOR
        else:
            return Level.BASEMENT

zones = ZoneParser.parse(scope.items, scope.itemRegistry)
logger.info("{} zones".format(len(zones)))
output = ''
for z in zones:
    output += '\n' + str(z)

logger.info(output)
