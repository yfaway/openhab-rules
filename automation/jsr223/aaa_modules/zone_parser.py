import re

from core import osgi
from core.jsr223 import scope
from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.neighbor import Neighbor, NeighborType
from aaa_modules.layout_model.zone import Zone, Level

from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition
from aaa_modules.layout_model.devices.astro_sensor import AstroSensor
from aaa_modules.layout_model.devices.camera import Camera
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
from aaa_modules.layout_model.devices.contact import Door
from aaa_modules.layout_model.devices.dimmer import Dimmer
from aaa_modules.layout_model.devices.gas_sensor import Co2GasSensor, NaturalGasSensor, SmokeSensor
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor
from aaa_modules.layout_model.devices.network_presence import NetworkPresence
from aaa_modules.layout_model.devices.plug import Plug
from aaa_modules.layout_model.devices.switch import Fan, Light
from aaa_modules.layout_model.devices.temperature_sensor import TemperatureSensor

META_DIMMING_SETTING = 'dimmable'

# A metadata item to indicate which light to turn off when the current light
# is switched on.
META_TURN_OFF_OTHER_LIGHT = 'turnOff'

# A meta data item to indicate that this light shouldn't be turned on when a
# motion event is triggered, if the other light is already on.
META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON = 'disableMotionTriggeringIfOtherLightIsOn'

# Indicates that the switch must not be turned on when the associated 
# motion sensor is triggered.
TAG_DISABLE_TRIGGERING_FROM_MOTION_SENSOR = "disable-triggering-from-motion-sensor"

# The light level threshold; if it is below this value, turn on the light.
ILLUMINANCE_THRESHOLD_IN_LUX = 8

TIME_OF_DAY_ITEM_NAME = 'VT_Time_Of_Day'

ITEM_NAME_PATTERN = '([^_]+)_([^_]+)_(.+)' # level_location_deviceName

ZONE_NAME_PATTERN = 'Zone_([^_]+)' # Zone_Name

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

class ZoneParser:
    '''
    Construct the zones from the existing items in OpenHab, using this naming
    convention: Floor_Location_ItemType
    For example, item "Switch FF_Foyer_LightSwitch ..." will create a zone named
    'Foyer' at the first floor; and the zone contains a Light object.

    See :class:`.ZoneManager` and :class:`.Zone`.
    '''

    def parse(self, items, itemRegistry):
        '''
        :param scope.items items:
        :param scope.itemRegistry itemRegistry:
        :rtype: list(Zone)
        '''
        zoneMap = {} # map from string zoneId to Zone

        # Each item is a list of 3 items: zone id, zone id, neighbor type.
        neighbors = [] 

        # pre-add all zone items
        for itemName in items.keys():
            match = re.search(ZONE_NAME_PATTERN, itemName)
            if not match:
                continue

            zoneName = match.group(1)
            (zone, localNeighbors) = self._createZone(itemName, zoneName)

            zoneMap[zone.getId()] = zone
            for n in localNeighbors:
                neighbors.append(n)

        # now add the items
        for itemName in items.keys():
            match = re.search(ITEM_NAME_PATTERN, itemName)
            if not match:
                continue

            levelString = match.group(1)
            location = match.group(2)
            deviceName = match.group(3)
            
            zoneId = self._getZoneIdFromItemName(itemName)
            if zoneId in zoneMap:
                zone = zoneMap[zoneId]
            else:
                zone = Zone(location, [], self._getZoneLevel(levelString))

            openHabItem = itemRegistry.getItem(itemName)

            zone = self._addCamera(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addDoor(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addNetworkPresence(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addSwitches(
                    deviceName, openHabItem, zone, itemRegistry, neighbors)
            zone = self._addPlugs(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addAlarmPartition(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addChromeCasts(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addHumiditySensors(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addTemperatureSensors(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addCo2Sensors(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addNaturalGasSensors(
                    deviceName, openHabItem, zone, itemRegistry)
            zone = self._addSmokeSensors(
                    deviceName, openHabItem, zone, itemRegistry)

            if len(zone.getDevices()) > 0:
                zoneMap[zoneId] = zone

            # end looping items

        astroSensor = AstroSensor(itemRegistry.getItem(TIME_OF_DAY_ITEM_NAME))
        for z in zoneMap.values():
            if len(z.getDevicesByType(Light)) > 0 or \
                    len(z.getDevicesByType(Dimmer)) > 0:
                z = z.addDevice(astroSensor)
                zoneMap[z.getId()] = z

        for neighborInfo in neighbors:
            zone = zoneMap[neighborInfo[0]]
            zone = zone.addNeighbor(Neighbor(neighborInfo[1], neighborInfo[2]))
            zoneMap[neighborInfo[0]] = zone

        return [self._normalizeNeighbors(z) for z in zoneMap.values()]

    def _addCamera(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Camera' == deviceName:
            camera = Camera(openHabItem, zone.getName())
            zone = self._addDeviceToZone(camera, zone)

        return zone

    def _addDoor(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Door' == deviceName:
            door = Door(openHabItem)
            zone = self._addDeviceToZone(door, zone)

        return zone

    def _addNetworkPresence(self, deviceName, openHabItem, zone, itemRegistry):
        if 'NetworkPresence' in deviceName:
            presence = NetworkPresence(openHabItem)
            zone = self._addDeviceToZone(presence, zone)

        return zone

    def _addAlarmPartition(self, deviceName, openHabItem, zone, itemRegistry):
        if 'AlarmPartition' == deviceName:
            itemName = openHabItem.getName()
            alarmModeItem = itemRegistry.getItem(itemName + '_ArmMode')

            alarm = AlarmPartition(openHabItem, alarmModeItem)
            zone = self._addDeviceToZone(alarm, zone)

        return zone

    def _addChromeCasts(self, deviceName, openHabItem, zone, itemRegistry):
        if 'ChromeCast' == deviceName:
            itemName = openHabItem.getName()

            sinkNameMeta = MetadataRegistry.get(
                    MetadataKey("sinkName", itemName)) 

            cast = ChromeCastAudioSink(itemName, sinkNameMeta.value)
            zone = zone.addDevice(cast)

        return zone

    def _addHumiditySensors(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Humidity' in deviceName:
            device = HumiditySensor(openHabItem)
            zone = self._addDeviceToZone(device, zone)

        return zone

    def _addTemperatureSensors(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Temperature' in deviceName:
            device = TemperatureSensor(openHabItem)
            zone = self._addDeviceToZone(device, zone)

        return zone

    def _addCo2Sensors(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Co2' == deviceName:
            stateItem = itemRegistry.getItem(openHabItem.getName() + 'State')

            device = Co2GasSensor(openHabItem, stateItem)
            zone = self._addDeviceToZone(device, zone)

        return zone

    def _addNaturalGasSensors(self, deviceName, openHabItem, zone, itemRegistry):
        if 'NaturalGas' == deviceName:
            stateItem = itemRegistry.getItem(openHabItem.getName() + 'State')

            device = NaturalGasSensor(openHabItem, stateItem)
            zone = self._addDeviceToZone(device, zone)

        return zone

    def _addSmokeSensors(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Smoke' == deviceName:
            stateItem = itemRegistry.getItem(openHabItem.getName() + 'State')

            device = SmokeSensor(openHabItem, stateItem)
            zone = self._addDeviceToZone(device, zone)

        return zone

    def _addPlugs(self, deviceName, openHabItem, zone, itemRegistry):
        if 'Plug' == deviceName:
            itemName = openHabItem.getName()
            
            powerItemName = itemName + '_Power'
            if powerItemName in scope.items:
                powerItem = itemRegistry.getItem(itemName + '_Power')
            else:
                powerItem = None

            plug = Plug(openHabItem, powerItem)
            zone = self._addDeviceToZone(plug, zone)

        return zone

    def _addSwitches(self, deviceName, openHabItem, zone, itemRegistry, neighbors):
        itemName = openHabItem.getName()
        zoneId = zone.getId()

        if 'LightSwitch' == deviceName:
            # open space relationship
            turnOffMeta = MetadataRegistry.get(
                    MetadataKey(META_TURN_OFF_OTHER_LIGHT, itemName)) 
            if None != turnOffMeta:
                neighborZoneId = self._getZoneIdFromItemName(
                        turnOffMeta.value)

                neighbor = [zoneId, neighborZoneId, NeighborType.OPEN_SPACE]
                neighbors.append(neighbor)

            # master-slave open space relationship
            masterSlaveMeta = MetadataRegistry.get(
                    MetadataKey(META_DISABLE_MOTION_TRIGGERING_IF_OTHER_LIGHT_IS_ON,
                        itemName)) 
            if None != masterSlaveMeta:
                masterZoneId = self._getZoneIdFromItemName(masterSlaveMeta.value)

                neighborForward = [masterZoneId, zoneId, NeighborType.OPEN_SPACE_SLAVE]
                neighbors.append(neighborForward)

                neighborReverse = [zoneId, masterZoneId, NeighborType.OPEN_SPACE_MASTER]
                neighbors.append(neighborReverse)

            disableMotionSensorTriggering = openHabItem.hasTag(
                    TAG_DISABLE_TRIGGERING_FROM_MOTION_SENSOR)

            durationMeta = MetadataRegistry.get(
                    MetadataKey('durationInMinutes', itemName)) 
            if None != durationMeta:
                durationInMinutes = int(durationMeta.value)
            else:
                raise ValueError(
                        'Missing durationInMinutes value for {}'.format(itemName))

            # dimmer setting
            meta = MetadataRegistry.get(
                    MetadataKey(META_DIMMING_SETTING, itemName)) 
            if None != meta:
                config = meta.configuration
                level = config['level'].intValue()
                timeRanges = config['timeRanges']

                switch = Dimmer(openHabItem, durationInMinutes, level, timeRanges,
                        ILLUMINANCE_THRESHOLD_IN_LUX,
                        disableMotionSensorTriggering)
            else:
                switch = Light(openHabItem, durationInMinutes, 
                        ILLUMINANCE_THRESHOLD_IN_LUX,
                        disableMotionSensorTriggering)

            zone = zone.addDevice(switch)
        elif 'FanSwitch' == deviceName:
            durationMeta = MetadataRegistry.get(
                    MetadataKey('durationInMinutes', itemName)) 
            if None != durationMeta:
                durationInMinutes = int(durationMeta.value)
            else:
                raise ValueError(
                        'Missing durationInMinutes value for {}'.format(itemName))

            fan = Fan(openHabItem, durationInMinutes)
            zone = zone.addDevice(fan)
        elif 'LightSwitch_Illuminance' == deviceName:
            illuminanceSensor = IlluminanceSensor(openHabItem)
            zone = self._addDeviceToZone(illuminanceSensor, zone)
        elif deviceName.endswith('MotionSensor'):
            motionSensor = MotionSensor(openHabItem)
            zone = self._addDeviceToZone(motionSensor, zone)

        return zone

    def _normalizeNeighbors(self, zone):
        '''
        If a zone has the same neighbor with more than one OPEN_SPACE type,
        remove the generic one NeighborType.OPEN_SPACE

        :rtype: Zone new object
        '''
        zoneIdToType = {}
        for neighbor in zone.getNeighbors():
            zoneId = neighbor.getZoneId()
            if zoneId in zoneIdToType:
                types = zoneIdToType[zoneId]
            else:
                types = []
                zoneIdToType[zoneId] = types

            types.append(neighbor.getType())

        for types in zoneIdToType.values():
            if NeighborType.OPEN_SPACE_MASTER in types \
                or NeighborType.OPEN_SPACE_SLAVE in types:
                if NeighborType.OPEN_SPACE in types:
                    types.remove(NeighborType.OPEN_SPACE)

        zone = Zone(zone.getName(), zone.getDevices(), zone.getLevel(), [],
                {}, zone.isExternal(), zone.getDisplayIcon(), zone.getDisplayOrder())
        for zoneId in zoneIdToType.keys():
            for type in zoneIdToType[zoneId]:
                zone = zone.addNeighbor(Neighbor(zoneId, type))

        return zone

    def _getZoneIdFromItemName(self, itemName):
        '''
        :rtype: str
        '''
        match = re.search(ITEM_NAME_PATTERN, itemName)
        if not match:
            raise ValueError('Invalid item name pattern: ' + itemName)

        levelString = match.group(1)
        location = match.group(2)

        return str(self._getZoneLevel(levelString)) + '_' + location
                
    def _getZoneLevel(self, levelString):
        '''
        :rtype: Level 
        '''
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

    def _createZone(self, itemName, zoneName):
        '''
        :return: the zone associated with the itemName
        :rtype: Zone
        '''
        levelMeta = MetadataRegistry.get(MetadataKey('level', itemName)) 
        if None == levelMeta:
            raise ValueError('The zone level must be specified as BM, FF, SF, or TF')

        level = self._getZoneLevel(levelMeta.value)

        externalMeta = MetadataRegistry.get(MetadataKey('external', itemName)) 
        external = None != externalMeta and "true" == externalMeta.value.lower()

        displayIconMeta = MetadataRegistry.get(MetadataKey('displayIcon', itemName)) 
        if None != displayIconMeta:
            displayIcon = displayIconMeta.value
        else:
            displayIcon = None

        displayOrderMeta = MetadataRegistry.get(MetadataKey('displayOrder', itemName)) 
        if None != displayOrderMeta:
            displayOrder = int(displayOrderMeta.value)
        else:
            displayOrder = 9999

        zone = Zone(zoneName, [], level, [], {}, external, displayIcon, displayOrder)

        neighbors = []

        openSpaceMeta = MetadataRegistry.get(
                MetadataKey('openSpaceNeighbors', itemName))
        if None != openSpaceMeta:
            for neighborId in openSpaceMeta.value.split(','):
                neighborId = neighborId.strip()
                neighbors.append([zone.getId(), neighborId, NeighborType.OPEN_SPACE])
            
        return [zone, neighbors]

    def _addDeviceToZone(self, device, zone):
        '''
        Helper method to retrieve additional device through the meta, and then
        add the device to the given zone.

        :return: a new zone containing the device.
        '''
        wifiMeta = MetadataRegistry.get(MetadataKey('wifi', device.getItemName()))
        if None != wifiMeta and "true" == wifiMeta.value.lower():
            device = device.setUseWifi(True)

        batteryPoweredMeta = MetadataRegistry.get(MetadataKey('batteryPowered',
                    device.getItemName()))
        if None != batteryPoweredMeta and "true" == batteryPoweredMeta.value.lower():
            device = device.setBatteryPowered(True)

        autoReportMeta = MetadataRegistry.get(MetadataKey('autoReport',
                    device.getItemName()))
        if None != autoReportMeta and "true" == autoReportMeta.value.lower():
            device = device.setAutoReport(True)

        return zone.addDevice(device)

zones = ZoneParser().parse(scope.items, scope.itemRegistry)
output = "{} zones".format(len(zones))
for z in zones:
    output += '\n' + str(z)
#PE.logInfo(output)
