import re

from core import osgi
from core.jsr223 import scope
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from org.slf4j import Logger, LoggerFactory

from aaa_modules.layout_model import zone
reload(zone)

from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.zone import Zone, Level
from aaa_modules.layout_model.astro_sensor import AstroSensor
from aaa_modules.layout_model.dimmer import Dimmer
from aaa_modules.layout_model.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.motion_sensor import MotionSensor
from aaa_modules.layout_model.switch import Fan, Light

META_DIMMING_SETTING = 'dimmable'

# A metadata item to indicate which light to turn off when the current light
# is switched on.
META_TURN_OFF_OTHER_LIGHT = 'turnOff'

# A meta data item to indicate that this light shouldn't be turned on when a
# motion event is triggered, if the other light is already on.
META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON = 'disableMotionTriggeringIfOtherLightIsOn'

# The light level threshold; if it is below this value, turn on the light.
ILLUMINANCE_THRESHOLD_IN_LUX = 8

TIME_OF_DAY_ITEM_NAME = 'VT_Time_Of_Day'

ITEM_NAME_PATTERN = '([^_]+)_([^_]+)_(.+)' # level_location_deviceName

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
        zoneMap = {} # map from string zoneId to Zone

        # Each item is a list of 3 items: zone id, zone id, neighbort type.
        neighbors = [] 

        for itemName in items.keys():
            match = re.search(ITEM_NAME_PATTERN, itemName)
            if not match:
                continue

            levelString = match.group(1)
            location = match.group(2)
            deviceName = match.group(3)
            
            zoneId = ZoneParser.getZoneIdFromItemName(itemName)
            if zoneId in zoneMap:
                zone = zoneMap[zoneId]
            else:
                zone = Zone(location, [], ZoneParser.getZoneLevel(levelString))

            openHabItem = itemRegistry.getItem(itemName)
            if 'LightSwitch' == deviceName:
                # open space relationship
                turnOffMeta = MetadataRegistry.get(
                        MetadataKey(META_TURN_OFF_OTHER_LIGHT, itemName)) 
                if None != turnOffMeta:
                    neighborZoneId = ZoneParser.getZoneIdFromItemName(
                            turnOffMeta.value)

                    neighbor = [zoneId, neighborZoneId, NeighborType.OPEN_SPACE]
                    neighbors.append(neighbor)

                # master-slave open space relationship
                masterSlaveMeta = MetadataRegistry.get(
                        MetadataKey(META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON,
                            itemName)) 
                if None != masterSlaveMeta:
                    masterZoneId = ZoneParser.getZoneIdFromItemName(masterSlaveMeta.value)

                    neighborForward = [masterZoneId, zoneId, NeighborType.OPEN_SPACE_SLAVE]
                    neighbors.append(neighborForward)

                    neighborReverse = [zoneId, masterZoneId, NeighborType.OPEN_SPACE_MASTER]
                    neighbors.append(neighborReverse)

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
                zoneMap[zoneId] = zone

            # end looping items

        astroSensor = AstroSensor(itemRegistry.getItem(TIME_OF_DAY_ITEM_NAME))
        for z in zoneMap.values():
            if len(z.getDevicesByType(Light)) > 0 or \
                    len(z.getDevicesByType(Dimmer)) > 0:
                z.addDevice(astroSensor)

        for neighborInfo in neighbors:
            zone = zoneMap[neighborInfo[0]]
            neighbor = zoneMap[neighborInfo[1]]

            zone.addNeighbor(Neighbor(neighbor, neighborInfo[2]))

        return zoneMap.values()

    # @return string
    @staticmethod
    def getZoneIdFromItemName(itemName):
        match = re.search(ITEM_NAME_PATTERN, itemName)
        if not match:
            raise ValueError('Invalid item name pattern: ' + itemName)

        levelString = match.group(1)
        location = match.group(2)

        return str(ZoneParser.getZoneLevel(levelString)) + '_' + location
                
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
