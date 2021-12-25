import logging

from unittest import TestCase

from tdb.cardbot.mtgjson import MTGJson


logging.basicConfig(level=logging.DEBUG)


class TestMTGJson(TestCase):
    def test_download_meta(self):
        MTGJson.download_meta()

    def test_download_all_printings(self):
        MTGJson.download_all_printings()
