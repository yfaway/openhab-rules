import unittest
import time

from openhab.testing import run_test
from org.slf4j import Logger, LoggerFactory
from openhab.jsr223 import scope

from aaa_modules import cast_manager
reload(cast_manager)
from aaa_modules import cast_manager

LOGGER = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

# Unit tests for cast_manager.
class CastManagerTest(unittest.TestCase):
    def testPlayMessage_none_returnsFalse(self):
        result = cast_manager.playMessage(None)
        self.assertFalse(result)

    def testPlayMessage_emptyMessage_returnsFalse(self):
        result = cast_manager.playMessage('')
        self.assertFalse(result)

    def testPlayMessage_validMessage_returnsTrue(self):
        casts = cast_manager.getFirstFloorCasts()

        result = cast_manager.playMessage("hello world", casts)
        self.assertTrue(result)

        time.sleep(1) # sleep for 1 sec for the pause message to go through
        for cast in casts:
            self.assertFalse(cast.isActive())

    def testPlayStream_none_returnsFalse(self):
        result = cast_manager.playStream(None)
        self.assertFalse(result)

    def testPlayStream_emptyStreamName_returnsFalse(self):
        result = cast_manager.playStream("")
        self.assertFalse(result)

    def testPlayStream_invalidStreamName_returnsFalse(self):
        result = cast_manager.playStream("invalid name")
        self.assertFalse(result)

    def testPlayStream_validStreamName_returnsTrue(self):
        casts = cast_manager.getFirstFloorCasts()
        for cast in casts: # reset the stream first
            cast.setStream('', '')

        streams = cast_manager.getAllStreamNames()

        try:
            streamName = streams[0]
            result = cast_manager.playStream(streamName, casts)
            self.assertTrue(result)

            for cast in casts:
                self.assertEqual(streamName, cast.getStreamName())
                self.assertEqual(cast_manager.getStreamUrl(streamName), 
                        cast.getStreamUrl())
        finally:
            cast_manager.pause(casts)

    def testGetAllCasts_noParams_returnsNormally(self):
        casts = cast_manager.getAllCasts()
        self.assertTrue(len(casts) > 0)

        for cast in casts:
            self.assertTrue(cast.getPlayerName() in scope.items)
            self.assertTrue(cast.getVolumeName() in scope.items)
            self.assertTrue(cast.getIdleItemName() in scope.items)

    def testGetFirstFloorCasts_noParams_returnsNormally(self):
        casts = cast_manager.getFirstFloorCasts()
        self.assertTrue(len(casts) > 0)

    def testFindCasts_invalidPrefixString_returnsEmptyList(self):
        casts = cast_manager.findCasts("an invalid prefix");
        self.assertEqual(0, len(casts))

    def testFindCasts_invalidPrefixStringType_returnsEmptyList(self):
        casts = cast_manager.findCasts(scope.StringType("an invalid prefix"));
        self.assertEqual(0, len(casts))

    def testFindCasts_all_returnsAll(self):
        casts = cast_manager.getAllCasts()
        result = cast_manager.findCasts("ALL");
        self.assertEqual(len(casts), len(result))

    def testFindCasts_allStringType_returnsAll(self):
        casts = cast_manager.getAllCasts()
        result = cast_manager.findCasts(scope.StringType("ALL"));
        self.assertEqual(len(casts), len(result))

    def testFindCasts_null_returnsAll(self):
        casts = cast_manager.getAllCasts()
        result = cast_manager.findCasts(scope.UnDefType.NULL);
        self.assertEqual(len(casts), len(result))

    def testFindCasts_undef_returnsAll(self):
        casts = cast_manager.getAllCasts()
        result = cast_manager.findCasts(scope.UnDefType.UNDEF);
        self.assertEqual(len(casts), len(result))

    def testFindCasts_firstItemPrefix_returnsOne(self):
        casts = cast_manager.getAllCasts()
        result = cast_manager.findCasts(casts[0].getPrefix());
        self.assertEqual(1, len(result))
        self.assertEqual(casts[0], result[0]);

    def testGetStreamNames_noParams_returnsNonEmptyList(self):
        streams = cast_manager.getAllStreamNames()
        self.assertTrue(len(streams) > 0)

    def testGetStreamUrl_invalidName_returnsNone(self):
        url = cast_manager.getStreamUrl("invalid name")
        self.assertEqual(None, url)

    def testGetStreamUrl_validName_returnsNonEmptyString(self):
        streams = cast_manager.getAllStreamNames()
        url = cast_manager.getStreamUrl(streams[0])
        self.assertNotEqual(None, url)
        self.assertNotEqual('', url)

#run_test(CastManagerTest, LOGGER) 
