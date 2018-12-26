# Run all unit tests.

import unittest

from org.slf4j import Logger, LoggerFactory

from aaa_modules import alert_test
reload(alert_test)
from aaa_modules.alert_test import AlertTest

from aaa_modules import alert_manager_test
reload(alert_manager_test)
from aaa_modules.alert_manager_test import AlertManagerTest

from aaa_modules import chromecast_test
reload(chromecast_test)
from aaa_modules.chromecast_test import ChromeCastTest
    
from aaa_modules import cast_manager_test
reload(cast_manager_test)
from aaa_modules.cast_manager_test import CastManagerTest

from aaa_modules import camera_utilities_test
reload(camera_utilities_test)
from aaa_modules.camera_utilities_test import CameraUtilitiesTest

from aaa_modules import time_utilities_test
reload(time_utilities_test)
from aaa_modules.time_utilities_test import TimeUtilitiesTest

#import alert_sender_test
#reload(alert_sender_test)
#from alert_sender_test import AlertRuleTest

logger = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

TEST_NAMES = [
    AlertTest,
    AlertManagerTest,
    ChromeCastTest,
    CastManagerTest,
    #AlertRuleTest,
    CameraUtilitiesTest,
    TimeUtilitiesTest,
]

def getTestSuites():
    suites = []
    loader = unittest.TestLoader()

    for name in TEST_NAMES:
        suite = loader.loadTestsFromTestCase(name)
        suites.append(suite)

    return suites

def runTests():
    def _formatErrors(errors):
        return "[{}]".format(",\n    ".join('{{"name":"{}", "stack":"{}"}}'.format(
                        test.id(), stack.replace('"', r'\"')) for test, stack in errors))

    suites = unittest.TestSuite(getTestSuites())

    runner = unittest.TextTestRunner(resultclass=unittest.TestResult)
    result = runner.run(suites)

    logger.info("Run {} tests; {} errors, {} failures, {} skipped".format(
                result.testsRun, len(result.errors), len(result.failures),
                len(result.skipped)))

    if len(result.errors) > 0:
        logger.error(_formatErrors(result.errors))

    if len(result.failures) > 0:
        logger.error(_formatErrors(result.failures))

#runTests()
