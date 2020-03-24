import random
from threading import Timer

from aaa_modules.layout_model.zone import Level, ZoneEvent
from aaa_modules.layout_model.actions.action import Action
from aaa_modules.layout_model.alarm_partition import AlarmPartition
from aaa_modules.layout_model.devices.activity_times import ActivityTimes
from aaa_modules.layout_model.devices.chromecast_audio_sink import ChromeCastAudioSink
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

class SimulateDaytimePresence(Action):

    '''
    Play the provided URL stream when an external motion sensor is triggered
    and while the system is in arm-away mode, and when it is not sleep time.
    @todo: use local URL to avoid reliance on the Internet connection.
    '''

    def __init__(self, musicUrl, musicVolume = 80, playDurationInSeconds = None):
        '''
        Ctor

        :param str musicUrl: 
        :param int musicVolume: percentage from 0 to 100 
        :param int playDurationInSeconds: how long the music will be played. \
            If not specified, this value will be generated randomly.
        :raise ValueError: if any parameter is invalid
        '''

        if None == musicUrl:
            raise ValueError('musicUrl must be specified')

        self.musicUrl = musicUrl
        self.musicVolume = musicVolume
        self.playDurationInSeconds = playDurationInSeconds
        self.timer = None

    def onAction(self, eventInfo):
        zone = eventInfo.getZone()
        zoneManager = eventInfo.getZoneManager()

        if ZoneEvent.MOTION != eventInfo.getEventType():
            return False

        if not zone.isExternal():
            return False

        securityPartitions = zoneManager.getDevicesByType(AlarmPartition)
        if len(securityPartitions) == 0:
            return False

        if not securityPartitions[0].isArmedAway():
            return False

        # Get an audio sink from the first floor.
        audioSink = None
        zones = [z for z in zoneManager.getZones() if z.getLevel() == Level.FIRST_FLOOR]
        for z in zones:
            sinks = z.getDevicesByType(ChromeCastAudioSink)
            if len(sinks) > 0:
                audioSink = sinks[0]
                break

        if None == audioSink:
            return False

        activities = zoneManager.getDevicesByType(ActivityTimes)
        if len(activities) > 0:
            if activities[0].isSleepTime():
                return False

        audioSink.playStream(self.musicUrl, self.musicVolume)

        if None != self.timer:
            self.timer.cancel()

        durationInSeconds = self.playDurationInSeconds
        if None == durationInSeconds:
            durationInSeconds = random.randint(3 * 60, 10 * 60)

        self.timer = Timer(durationInSeconds, lambda : audioSink.pause())
        self.timer.start()

        PE.logInfo("Simulate daytime presence by playing music for {} seconds".format(
                    durationInSeconds))

        return True
