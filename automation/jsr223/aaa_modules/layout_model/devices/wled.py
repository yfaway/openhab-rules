import random
from threading import Timer
from core.jsr223 import scope
    
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.layout_model.devices.switch import Light

class Wled(Light):
    '''
    Represents a WLED strip.

    @see https://github.com/Skinah/wled
    @see https://github.com/Aircoookie/WLED
    '''

    def __init__(self, masterControlItem, effectItem, durationInMinutes):
        '''
        Constructs a new object.

        :raise ValueError: if any parameter is invalid
        '''
        Light.__init__(self, masterControlItem, durationInMinutes,
                0, True)

        self.effectItem = effectItem
        self.effectTimer = None

    def getEffects(self):
        return {0: 'Solid',
                102: 'Candle Multi',
                52: 'Circus', 
                34: 'Colorful',
                8:  'Colorloop',
                74: 'Colortwinkle',
                7:  'Dynamic',
                69: 'Fill Noise',
                45: 'Fire Flicker',
                89: 'Fireworks Starbust',
                110: 'Flow',
                87: 'Glitter',
                53: 'Halloween',
                75: 'Lake',
                44: 'Merry Christmas',
                107: 'Noise Pal',
                105: 'Phased',
                11: 'Rainbow',
                5:  'Random Colors',
                79: 'Ripple',
                99: 'Ripple Rainbow',
                15: 'Running',
                108: 'Sine',
                39: 'Stream',
                13: 'Theater'
        }

    def onSwitchTurnedOn(self, events, itemName):
        '''
        @override to turn on the effect timer
        '''
        super(Wled, self).onSwitchTurnedOn(events, itemName)

        self._startEffectTimer(events)

    def onSwitchTurnedOff(self, events, itemName):
        '''
        @override to turn off the effect timer
        '''
        super(Wled, self).onSwitchTurnedOff(events, itemName)

        self._cancelEffectTimer()

    def _startEffectTimer(self, events):

        '''
        Creates and returns the timer to change to a random effect
        '''
        def changeEffect():
            effectId = random.choice(self.getEffects().keys())
            events.sendCommand(self.effectItem.getName(), str(effectId))

            nextDurationInMinute = random.choice(range(3, 7))
            self.timer = Timer(nextDurationInMinute * 60, changeEffect)
            self.timer.start()

        self._cancelTimer() # cancel the previous timer, if any.

        nextDurationInMinute = random.choice(range(1, 3))
        self.timer = Timer(5, changeEffect) # start timer in 5 secs
        self.timer.start()

    def _cancelEffectTimer(self):
        '''
        Cancel the random effect switch timer.
        '''
        if None != self.effectTimer and self.effectTimer.isAlive():
            self.effectTimer.cancel()
            self.effectTimer = None

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}".format(super(Wled, self).__unicode__())
