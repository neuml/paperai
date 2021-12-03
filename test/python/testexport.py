"""
Export module tests
"""

import unittest

from paperai.export import Export

# pylint: disable=C0411
from utils import Utils


class TestExport(unittest.TestCase):
    """
    Export tests
    """

    def testRun(self):
        """
        Test export run
        """

        Export.run(Utils.PATH + "/export.txt", Utils.PATH)
        self.assertEqual(
            Utils.hashfile(Utils.PATH + "/export.txt"),
            "ac15a3ece486c3035ef861f6706c3e1b",
        )
