# Run all unit tests.

import unittest

from aaa_modules.alert_test import AlertTest
from aaa_modules.alert_manager_test import AlertManagerTest
from aaa_modules.chromecast_test import ChromeCastTest
from aaa_modules.cast_manager_test import CastManagerTest
from aaa_modules.camera_utilities_test import CameraUtilitiesTest
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE
from aaa_modules.time_utilities_test import TimeUtilitiesTest

TEST_NAMES = [
    AlertTest,
    AlertManagerTest,
    ChromeCastTest,
    CastManagerTest,
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

    PE.logInfo("Run {} tests; {} errors, {} failures, {} skipped".format(
                result.testsRun, len(result.errors), len(result.failures),
                len(result.skipped)))

    if len(result.errors) > 0:
        PE.logInfo(_formatErrors(result.errors))

    if len(result.failures) > 0:
        PE.logInfo(_formatErrors(result.failures))

#runTests()
