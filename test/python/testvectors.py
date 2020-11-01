"""
Vectors module tests
"""

import os
import unittest

# pylint: disable=E0401
from paperai.vectors import RowIterator, Vectors

from utils import Utils

class TestVectors(unittest.TestCase):
    """
    Vectors tests
    """

    def testStream(self):
        """
        Test row streaming
        """

        # Full index stream
        self.assertEqual(len(list(RowIterator(Utils.DBFILE))), 34222)

    def testTokens(self):
        """
        Test tokens file creation
        """

        output = Vectors.tokens(Utils.DBFILE)
        self.assertEqual(Utils.hashfile(output), "9fb9b7088bb84930f0cf73d69cb58fe8")

    def testRun(self):
        """
        Tests word vectors creation
        """

        # Build vectors file
        Vectors.run(Utils.PATH, 300, 4, Utils.PATH + "/test")
        self.assertTrue(os.path.getsize(Utils.PATH + "/test.magnitude") > 0)
