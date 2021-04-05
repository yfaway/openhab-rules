Items with the "Out" prefix is used by the rules purely for displaying purpose in sitemaps only.
The rules will set the appropriate values.

See [ZoneParser document](https://github.com/yfaway/zone-apis/blob/master/zone_apis/aaa_modules/zone_parser.py)
for the latest naming convention. The current convention snapshot is pasted below.

1. The zones are defined as a String item with this pattern Zone_{name}:
        String Zone_GreatRoom                                                           
            { level="FF", displayIcon="player", displayOrder="1",                         
              openSpaceSlaveNeighbors="FF_Kitchen" } 
      - The levels are the reversed mapping of the enums in Zone::Level.
      - Here are the list of supported attributes: level, external, openSpaceNeighbors,
        openSpaceMasterNeighbors, openSpaceSlaveNeighbors, displayIcon, displayOrder.
       
2. The individual OpenHab items are named after this convention:
        {zone_id}_{device_type}_{device_name}.
    Here's an example:
        Switch FF_Office_LightSwitch "Office Light"
            [shared-motion-sensor]                                                        
            { channel="zwave:device:9e4ce05e:node8:switch_binary",                        
              turnOff="FF_Foyer_LightSwitch",                                             
              durationInMinutes="15" } 
