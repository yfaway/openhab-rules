from collections import OrderedDict

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

from aaa_modules.layout_model.devices.contact import Contact, Door, Window	
from aaa_modules.layout_model.devices.gas_sensor import Co2GasSensor, NaturalGasSensor, SmokeSensor
from aaa_modules.layout_model.devices.humidity_sensor import HumiditySensor
from aaa_modules.layout_model.devices.motion_sensor import MotionSensor
from aaa_modules.layout_model.devices.illuminance_sensor import IlluminanceSensor
from aaa_modules.layout_model.devices.plug import Plug
from aaa_modules.layout_model.devices.switch import Fan, Light
from aaa_modules.layout_model.devices.temperature_sensor import TemperatureSensor
from aaa_modules.layout_model.devices.tv import Tv

def generate(zm):
    '''
    Returns a string containing the sitemap frames for all the zones.
    
    :param ZoneManager zm:
    :rtype: str
    '''
    globalStr = ''
    for z in zm.getZones():
        itemCount = 0

        if z.getDisplayIcon() == None:
            zoneIcon = ''
        else:
            zoneIcon = z.getDisplayIcon()

        str = 'Text label="{}" icon="{}" {{\n'.format(z.getName(), zoneIcon)
        str += '  Frame label="{}" {{\n'.format(z.getName())

        # retain key order
        mappings = OrderedDict([
            (TemperatureSensor, 'Text item={} icon="temperature"'),
            (HumiditySensor, 'Text item={} icon="humidity"'),
            (Door, 'Text item={} icon="door"'),
            (Light, 'Switch item={} icon="light"'),
            (Fan,  'Switch item={} icon="fan"'),
            (Plug, 'Switch item={} icon="poweroutlet"'),
            (IlluminanceSensor, 'Text item={}'),
            (MotionSensor, 'Switch item={}'), 
            (Co2GasSensor, 'Text item={} icon="carbondioxide"'),
            (NaturalGasSensor, 'Text item={} icon="gas"'),
            (SmokeSensor, 'Text item={} icon="fire"'),
            (Tv, 'Switch item={} icon="screen"'),
        ])

        for cls in mappings.keys():
            itemString = '    {}\n'.format(mappings[cls])
            
            for d in z.getDevicesByType(cls):
                str += itemString.format(d.getItemName())
                itemCount += 1

        str += '  }\n'
        str += '}\n'

        if itemCount > 0:
            globalStr += str

    return globalStr

#PE.logInfo(generate(zm))
