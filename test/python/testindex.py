"""
Index module tests
"""

import unittest

# pylint: disable=E0401
from paperai.index import Index

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
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 0))), 21478)

        # Partial index stream - top n documents by entry date
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 10))), 224)
