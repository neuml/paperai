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
        self.assertEqual(Utils.hashfile(Utils.PATH + "/export.txt"), "a6f85df295a19f2d3c1a10ec8edce6ae")
