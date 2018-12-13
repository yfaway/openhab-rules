# Run all unit tests.

import unittest

from org.slf4j import Logger, LoggerFactory

from aaa_modules import chromecast_test
reload(chromecast_test)
from aaa_modules.chromecast_test import ChromeCastTest
    
from aaa_modules import cast_manager_test
reload(cast_manager_test)
from aaa_modules.cast_manager_test import CastManagerTest

LOGGER = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

TEST_NAMES = [ChromeCastTest, CastManagerTest]

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

    LOGGER.info("Run {} tests; {} errors, {} failures, {} skipped".format(
                result.testsRun, len(result.errors), len(result.failures),
                len(result.skipped)))

    if len(result.errors) > 0:
        LOGGER.error(_formatErrors(result.errors))

    if len(result.failures) > 0:
        LOGGER.error(_formatErrors(result.failures))

runTests()