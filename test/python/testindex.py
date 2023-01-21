"""
Index module tests
"""

import os
import tempfile
import unittest

from paperai.index import Index

# pylint: disable=C0411
from utils import Utils


class TestIndex(unittest.TestCase):
    """
    Index tests
    """

    def testConfig(self):
        """
        Test configuration
        """

        # Test YAML config
        config = os.path.join(tempfile.gettempdir(), "testconfig.yml")

        with open(config, "w", encoding="utf-8") as output:
            output.write("path: sentence-transformers/all-MiniLM-L6-v2")

        self.assertEqual(
            Index.config(config), {"path": "sentence-transformers/all-MiniLM-L6-v2"}
        )

        # Test word vectors
        self.assertEqual(
            Index.config(Utils.VECTORFILE),
            {"path": Utils.VECTORFILE, "scoring": "bm25", "pca": 3, "quantize": True},
        )

        # Test default
        self.assertEqual(
            Index.config("sentence-transformers/all-MiniLM-L6-v2"),
            {"path": "sentence-transformers/all-MiniLM-L6-v2"},
        )
        self.assertEqual(Index.config(None), None)

    def testStream(self):
        """
        Test row streaming
        """

        # Full index stream
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 0, True))), 29218)

        # Partial index stream - top n documents by entry date
        self.assertEqual(len(list(Index.stream(Utils.DBFILE, 10, True))), 287)
