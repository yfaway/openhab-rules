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

class ChromeCastTest(unittest.TestCase):
    def test_ctor(self):
        cast = ChromeCast(PREFIX, SINK)

        self.assertEqual(PREFIX, cast.getPrefix())
        self.assertEqual(SINK, cast.getSinkName())
        self.assertEqual(None, cast.getStreamUrl())
        self.assertEqual(None, cast.getStreamName())

        self.assertEqual(PREFIX + "Player", cast.getPlayerName())
        self.assertEqual(PREFIX + "Volume", cast.getVolumeName())
        self.assertEqual(PREFIX + "Idling", cast.getIdleItemName())

    def test_setStream(self):
        cast = ChromeCast(PREFIX, SINK)
        cast.setStream(STREAM_NAME, STREAM_URL)
        self.assertEqual(STREAM_URL, cast.getStreamUrl())
        self.assertEqual(STREAM_NAME, cast.getStreamName())

#run_test(ChromeCastTest, LOGGER) 
