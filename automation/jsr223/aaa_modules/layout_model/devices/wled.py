from core.jsr223 import scope
    
from aaa_modules.layout_model.devices.switch import Light

class Wled(Light):
    '''
    Represents a WLED strip.

    @see https://github.com/Skinah/wled
    @see https://github.com/Aircoookie/WLED
    '''

    def __init__(self, masterControlItem, durationInMinutes):
        '''
        Constructs a new object.

        :raise ValueError: if any parameter is invalid
        '''
        Light.__init__(self, masterControlItem, durationInMinutes,
                0, True)

    def getEffects(self):
        return ['Solid',
                'Circus', 
                'Glitter',
                'Halloween',
                'Lake',
                'Merry Christmas'
        ]

    def turnOn(self, events):
        '''
        Invoke the super class to turn on the light and start a turn-off timer.
        In addition, start a separte timer with a randomized period to set a
        random effect.

        @override
        '''
        super(Wled, self).turnOn(events)

    def __unicode__(self):
        '''
        @override
        '''
        return u"{}".format(super(Wled, self).__unicode__())
