"""
Index module tests
"""

import unittest

from paperai.index import Index

# pylint: disable=C0411
from utils import Utils


class TestIndex(unittest.TestCase):
    """
    Index tests
    """

    def testStream(self):
        """
        Test row streaming
        """

        # Full index stream
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 0, True))), 29218)

        # Partial index stream - top n documents by entry date
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 10, True))), 287)
