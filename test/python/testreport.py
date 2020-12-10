"""
Report module tests
"""

import os
import unittest

# pylint: disable=E0401
from paperai.report.execute import Execute

from utils import Utils

class TestReport(unittest.TestCase):
    """
    Report tests
    """

    @unittest.skipIf(os.name == "nt", "Faiss not installed on Windows")
    def testReport1(self):
        """
        Runs test queries from report1.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report1.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report1.yml", 10, "md", Utils.PATH, None)

        hashes = [("Age.csv", "a840643fa1dd0fa43e00091a44880fb9"),
                  ("Heart Disease.csv", "6faff786d5a6b7fb1617a1057f973c58"),
                  ("Heart Failure.csv", "20a6801161f3302d640323003a79f6c8"),
                  ("Report1.md", "69cbf92ca92c45ef78d519aed2e59ca1")]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)

    @unittest.skipIf(os.name == "nt", "Faiss not installed on Windows")
    def testReport2(self):
        """
        Runs test queries from report2.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report2.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report2.yml", 10, "md", Utils.PATH, None)

        hashes = [("Match.csv", "2def38a008f33f25d7ab4a763d159e80"),
                  ("MatchSurround.csv", "e9f581d19b8802822f47261bce0e91b1"),
                  ("Section.csv", "7ae8b295f0d959ba12410807db7b7e48"),
                  ("Surround.csv", "fed9fb4249bf2f73fa9822753d359207"),
                  ("Report2.md", "9218fe80fe5e9fdd50c5719f54c52061")]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)

    @unittest.skipIf(os.name == "nt", "Faiss not installed on Windows")
    def testReport3(self):
        """
        Runs test queries from report3.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report3.yml", 1, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "md", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "ant", Utils.PATH, None, Utils.PATH)

        hashes = [("AI.csv", "b47e96639a210d2089a5bd4e7e7bfc98"),
                  ("Report3.md", "1a47340bc135fc086160c62f8731edee")]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)
