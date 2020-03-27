from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.action import Action
from aaa_modules.layout_model.devices.alarm_partition import AlarmPartition
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink

class TurnOffDevicesOnAlarmModeChange(Action):

    '''
    Turn off all the lights and audio devices if the house is armed-away or
    if the house is disarm (from armed-away mode). The later is needed as
    there are some rules that simulate presences using a combination of 
    lights/audio sinks.
    '''

    def __init__(self):
        pass

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.PARTITION_ARMED_AWAY, ZoneEvent.PARTITION_DISARMED_FROM_AWAY]

    def onAction(self, eventInfo):
        if not super(TurnOffDevicesOnAlarmModeChange, self).onAction(eventInfo):
            return False

        events = eventInfo.getEventDispatcher()
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        for z in zoneManager.getZones():
            z.turnOffLights(events)

        audioSinks = zoneManager.getDevicesByType(ChromeCastAudioSink)
        for s in audioSinks:
            s.pause()

        return True
