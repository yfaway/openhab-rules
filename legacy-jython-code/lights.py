from core import osgi
from core.rules import rule
from core.triggers import when

scriptExtension.importPreset("RuleSupport")
scriptExtension.importPreset("RuleSimple")

@rule("Update light-on time")
#@when("System started")
@when("Item VT_Time_Of_Day changed")
def setLightOnTime(event):
  state = items["VT_Time_Of_Day"]
  if state == StringType("EVENING") or state == StringType("NIGHT") \
        or state == StringType("BED"):
    events.sendCommand("VT_Time_LightOn", "ON")
  else:
    events.sendCommand("VT_Time_LightOn", "OFF")

# TODO remove when @when supports "System started".
setLightOnTime(None)
