import time
from threading import Timer

from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.device import Device

class Switch(Device):
    '''
    Represents a light or fan switch. Each switch contains an internal timer.
    When the switch is turned on, the timer is started. As the timer expires,
    the switch is turned off (if it is not off already). If the
    switch is turned off not by the timer, the timer is cancelled.
    '''

    def __init__(self, switchItem, durationInMinutes, 
            disableTrigeringFromMotionSensor = False):
        '''
        Ctor

        :param org.eclipse.smarthome.core.library.items.SwitchItem switchItem:
        :param int durationInMinutes: how long the switch will be kept on
        :param bool disableTrigeringFromMotionSensor: a flag to indicate whether \
            the switch should be turned on when motion sensor is triggered.\
            There is no logic associate with this value in this class; it is \
            used by external classes through the getter.
        :raise ValueError: if any parameter is invalid
        '''
        Device.__init__(self, switchItem)

        self.disableTrigeringFromMotionSensor = disableTrigeringFromMotionSensor
        self.lastOffTimestampInSeconds = -1

        self.durationInMinutes = durationInMinutes
        self.timer = None

    def _startTimer(self, events):
        '''
        Creates and returns the timer to turn off the switch.
        '''
        def turnOffSwitch():
            zone = self.getZoneManager().getContainingZone(self)

            (occupied, device) = zone.isOccupied([Fan, Light], 60)
            if not occupied:
                events.sendCommand(self.getItemName(), "OFF")
                PE.logDebug("{}: turning off {}.".format(
                            zone.getName(), self.getItemName()))
            else:
                self.timer = Timer(self.durationInMinutes * 60, turnOffSwitch)
                self.timer.start()

                PE.logDebug("{}: {} is in use by {}.".format(
                            zone.getName(), self.getItemName(), device))


        self._cancelTimer() # cancel the previous timer, if any.

        self.timer = Timer(self.durationInMinutes * 60, turnOffSwitch)
        self.timer.start()

    def _cancelTimer(self):
        '''
        Cancel the turn-off-switch timer.
        '''
        if None != self.timer and self.timer.isAlive():
            self.timer.cancel()
            self.timer = None

    def _isTimerActive(self):
        return None != self.timer and self.timer.isAlive()

    def turnOn(self, events):
        '''
        Turns on this light, if it is not on yet. In either case, the associated
        timer item is also turned on.
        '''
        if self.isOn(): # already on, renew timer
            self._startTimer(events)
        else: 
            events.sendCommand(self.getItemName(), "ON")

    def turnOff(self, events):
        '''
        Turn off this light.
        '''
        if self.isOn():
            events.sendCommand(self.getItemName(), "OFF")

        self._cancelTimer()

    def isOn(self):
        '''
        Returns true if the switch is turned on; false otherwise.
        '''
        return PE.isInStateOn(self.getItem().getState())

    def onSwitchTurnedOn(self, events, itemName):
        '''
        Invoked when a switch on event is triggered. Note that a switch can be
        turned on through this class' turnOn method, or through the event bus, or
        manually by the user.
        The following actions are done:
        - the on timestamp is set;
        - the timer is started or renewed.

        :param scope.events events 
        :param string itemName: the name of the item triggering the event
        :return True: if itemName refers to this switch; False otherwise
        '''
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            self._handleCommonOnAction(events)

        return isProcessed

    def onSwitchTurnedOff(self, events, itemName):
        '''
        Invoked when a switch off event is triggered. Note that a switch can be
        turned off through this class' turnOff method, or through the event bus,
        or manually by the user.
        The following actions are done:
        - the timer is cancelled.

        :param scope.events events: 
        :param string itemName: the name of the item triggering the event
        :return: True if itemName refers to this switch; False otherwise
        '''
        isProcessed = (self.getItemName() == itemName)
        if isProcessed:
            self.lastOffTimestampInSeconds = time.time()
            self._cancelTimer()

        return isProcessed

    def getLastOffTimestampInSeconds(self):
        '''
        Returns the timestamp in epoch seconds the switch was last turned off.

        :return: -1 if the timestamp is not available, or an integer presenting\
        the epoch seconds
        '''
        return self.lastOffTimestampInSeconds

    def canBeTriggeredByMotionSensor(self):
        '''
        Returns True if this switch can be turned on when a motion sensor is
        triggered.
        A False value might be desired if two switches share the same motion
        sensor, and only one switch shall be turned on when the motion sensor is
        triggered.

        :rtype: bool
        '''
        return not self.disableTrigeringFromMotionSensor

    # Misc common things to do when a switch is turned on.
    def _handleCommonOnAction(self, events):
        self.lastLightOnSecondSinceEpoch = time.time()
        
        self._startTimer(events) # start or renew timer

    def isLowIlluminance(self, currentIlluminance):
        ''' Always return False.  '''
        return False

    def __unicode__(self):
        ''' @override '''
        return u"{}".format(
                super(Switch, self).__unicode__())


class Light(Switch):
    ''' Represents a regular light.  '''

    def __init__(self, switchItem, durationInMinutes, illuminanceLevel = None,
            disableTrigeringFromMotionSensor = False):
        '''
        :param int illuminanceLevel: the illuminance level in LUX unit. The \
            light should only be turned on if the light level is below this unit.
        '''
        Switch.__init__(self, switchItem, durationInMinutes, 
                disableTrigeringFromMotionSensor)
        self._illuminanceLevel = illuminanceLevel

    def getIlluminanceThreshold(self):
        '''
        Returns the illuminance level in LUX unit. Returns None if not applicable.

        :rtype: int or None
        '''
        return self._illuminanceLevel

    def isLowIlluminance(self, currentIlluminance):
        '''
        Returns False if this light has no illuminance threshold or if 
        currentIlluminance is less than 0. Otherwise returns True if the
        currentIlluminance is less than threshold.
        @override
        '''
        if None == self.getIlluminanceThreshold():
            return False

        if currentIlluminance < 0: # current illuminance not available
            return False

        return currentIlluminance < self.getIlluminanceThreshold()

    def isOccupied(self, secondsFromLastEvent = 5 * 60):
        '''
        Returns True if the device is on.
        @override

        :rtype: bool
        '''
        return self.isOn();

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}, illuminance: {}".format(
                super(Light, self).__unicode__(), self._illuminanceLevel)

class Fan(Switch):
    ''' Represents a fan switch.  '''
    def __init__(self, switchItem, durationInMinutes):
        Switch.__init__(self, switchItem, durationInMinutes)
