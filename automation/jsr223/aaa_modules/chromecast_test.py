import unittest
from openhab.testing import run_test
from org.slf4j import Logger, LoggerFactory

from aaa_modules import chromecast
reload(chromecast)
from aaa_modules.chromecast import *

LOGGER = LoggerFactory.getLogger("org.eclipse.smarthome.model.script.Rules")

PREFIX = "cast_item_"
SINK = "sink"
STREAM_URL = "a stream"
STREAM_NAME = "a stream name"
TTS_MESSAGE = 'hello world'

class ChromeCastTest(unittest.TestCase):
    def test_ctor(self):
        cast = ChromeCast(PREFIX, SINK)

        self.assertEqual(PREFIX, cast.getPrefix())
        self.assertEqual(SINK, cast.getSinkName())
        self.assertEqual(None, cast.getStreamUrl())
        self.assertEqual(None, cast.getStreamName())
        self.assertEqual(None, cast.getLastTtsMessage())

        self.assertEqual(PREFIX + "Player", cast.getPlayerName())
        self.assertEqual(PREFIX + "Volume", cast.getVolumeName())
        self.assertEqual(PREFIX + "Idling", cast.getIdleItemName())

    def testSetStream_validValues_returnsNormally(self):
        cast = ChromeCast(PREFIX, SINK)
        cast.setStream(STREAM_NAME, STREAM_URL)
        self.assertEqual(STREAM_URL, cast.getStreamUrl())
        self.assertEqual(STREAM_NAME, cast.getStreamName())

    def testSetLastTtsMessage_validValues_returnsNormally(self):
        cast = ChromeCast(PREFIX, SINK)
        cast._setLastTtsMessage(TTS_MESSAGE)
        self.assertEqual(TTS_MESSAGE, cast.getLastTtsMessage())

#run_test(ChromeCastTest, LOGGER) 
