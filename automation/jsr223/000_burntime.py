# Origin of script: https://community.openhab.org/t/solved-jython-jsr223-not-properly-initialised-during-startup/46031/6
# Issue: https://github.com/eclipse/smarthome/issues/4324
# This script works around an init issue above that causes this error:
#   TypeError: can't set attributes of built-in/extension type 'NoneType' in <script> at line number 3

import time

from org.slf4j import Logger, LoggerFactory

log = LoggerFactory.getLogger("org.eclipse.smarthome.automation")

log.info("jsr223: checking for initialised context")

while True:
    try:
        scriptExtension.importPreset("RuleSupport")
        if automationManager != None:
            break;
    except:
        pass

    log.info("jsr223: context not initialised yet. waiting 10 sec before checking again")
    time.sleep(40)

log.info("jsr223: done")
