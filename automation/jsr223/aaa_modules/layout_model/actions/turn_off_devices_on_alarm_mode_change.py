from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import action
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink

@action(events = [ZoneEvent.PARTITION_ARMED_AWAY, ZoneEvent.PARTITION_DISARMED_FROM_AWAY])
class TurnOffDevicesOnAlarmModeChange:

    '''
    Turn off all the lights and audio devices if the house is armed-away or
    if the house is disarm (from armed-away mode). The later is needed as
    there are some rules that simulate presences using a combination of 
    lights/audio sinks.
    '''

    def __init__(self):
        pass

    def onAction(self, eventInfo):
        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        for z in zoneManager.getZones():
            z.turnOffLights(events)

        audioSinks = zoneManager.getDevicesByType(ChromeCastAudioSink)
        for s in audioSinks:
            s.pause()

        return True
