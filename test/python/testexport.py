"""
Export module tests
"""

import unittest

# pylint: disable=E0401
from paperai.export import Export

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
        self.assertEqual(Utils.hashfile(Utils.PATH + "/export.txt"), "ac15a3ece486c3035ef861f6706c3e1b")
