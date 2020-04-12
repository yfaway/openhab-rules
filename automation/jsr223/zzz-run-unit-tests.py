# Run all the unit tests.
# If there is any test failure, send an admin alert.
# The test output is always logged.

import time
import unittest

from core.rules import rule
from core.triggers import when

from aaa_modules.alert import Alert
from aaa_modules.alert_manager import AlertManager
from aaa_modules.platform_encapsulator import PlatformEncapsulator as PE

TEST_DISCOVERY_FOLDER = '/etc/openhab2/automation/jsr223/'
TEST_FILE_PATTERN = '*test.py'

@rule("Run unit tests daily at midnight.")
@when("Time cron 0 10 23 1/1 * ? *")
def runTests(event):
    def _formatErrors(errors):
        return "[{}]".format(",\n    ".join('{{"name":"{}", "stack":"{}"}}'.format(
                        test.id(), stack.replace('"', r'\"')) for test, stack in errors))

    loader = unittest.TestLoader()
    suites = unittest.TestSuite(
            loader.discover(TEST_DISCOVERY_FOLDER, TEST_FILE_PATTERN))

    runner = unittest.TextTestRunner(resultclass=unittest.TestResult)

    startTime = time.time()
    result = runner.run(suites)
    endTime = time.time()

    summary = "Run {} tests in {:.1f} seconds; {} errors, {} failures, {} skipped.".format(
            result.testsRun, (endTime - startTime), len(result.errors), len(result.failures),
            len(result.skipped))

    output = summary

    if len(result.errors) > 0:
        output += "\r\n" + _formatErrors(result.errors)

    if len(result.failures) > 0:
        output += "\r\n" + _formatErrors(result.failures)

    if len(result.errors) > 0 or len(result.failures) > 0:
        # Display summary again at the end for clarity.
        output += "\r\n\r\n" + summary

        subject = "[HA] {} failed unit tests".format(
                len(result.errors) + len(result.failures))
        alert = Alert.createInfoAlert(subject, output)
        if not AlertManager.processAdminAlert(alert):
            PE.logInfo('Failed to send unit test result.')

    PE.logInfo(output) # always log the test result even if there is no error.

#runTests(None)
