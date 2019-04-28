from aaa_modules.layout_model.switch import Light, Switch
from aaa_modules.layout_model.actions.action import Action

# Turns on a switch (fan, dimmer or regular light).
# If the switch is a dimmer or light, only turns it is evening time or if the
# illuminance is below a threshold.
class TurnOnSwitch(Action):
    def onAction(self, events, zone):
        isProcessed = False
        lightOnTime = zone.isLightOnTime()
        zoneIlluminance = zone.getIlluminanceLevel()

        for switch in zone.getDevicesByType(Switch):
            if isinstance(switch, Light):
                if (lightOnTime or
                        None == switch.getIlluminanceThreshold() or 
                        zoneIlluminance < switch.getIlluminanceThreshold()):
                    switch.turnOn(events)
                    isProcessed = True
            else:
                switch.turnOn(events)
                isProcessed = True
        
        return isProcessed
