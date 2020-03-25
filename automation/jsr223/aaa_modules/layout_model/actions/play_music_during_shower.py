from aaa_modules.layout_model.action import Action
from aaa_modules.layout_model.neighbor import NeighborType
from aaa_modules.layout_model.zone import ZoneEvent
from aaa_modules.layout_model.devices.activity_times import ActivityTimes
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class PlayMusicDuringShower(Action):

    '''
    Play the provided URL stream when the washroom fan is turned on. Pause
    when it it turned off.
    Won't play if it is sleep time. Otherwise, adjust the volume based on the
    current activity.
    '''

    def __init__(self, musicUrl):
        '''
        Ctor

        :param str musicUrl: 
        :raise ValueError: if any parameter is invalid
        '''

        if None == musicUrl:
            raise ValueError('musicUrl must be specified')

        self.musicUrl = musicUrl

    def getTriggeringEvents(self):
        '''
        :return: list of triggering events this action process.
        :rtype: list(ZoneEvent)
        '''
        return [ZoneEvent.SWITCH_TURNED_ON, ZoneEvent.SWITCH_TURNED_OFF]

    def onAction(self, eventInfo):
        if not super(PlayMusicDuringShower, self).onAction(eventInfo):
            return False

        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        # Get an audio sink from the current zone or a neighbor zone
        sinks = zone.getDevicesByType(ChromeCastAudioSink)
        if len(sinks) == 0:
            neighborZones = zone.getNeighborZones(zoneManager,
                    [NeighborType.OPEN_SPACE, NeighborType.OPEN_SPACE_MASTER,
                     NeighborType.OPEN_SPACE_SLAVE])
            for z in neighborZones:
                sinks = z.getDevicesByType(ChromeCastAudioSink)
                if len(sinks) > 0:
                    break

            if len(sinks) == 0:
                return False

        activity = None
        if None != zoneManager:
            activities = zoneManager.getDevicesByType(ActivityTimes)
            if len(activities) > 0:
                activity = activities[0]

                if activity.isSleepTime():
                    return False

        if ZoneEvent.SWITCH_TURNED_ON == eventInfo.getEventType():
            volume = 25 if (None != activity and activity.isQuietTime()) else 35
            sinks[0].playStream(self.musicUrl, volume)
        elif ZoneEvent.SWITCH_TURNED_OFF == eventInfo.getEventType():
            sinks[0].pause()

        return True
