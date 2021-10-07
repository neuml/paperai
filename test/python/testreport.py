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

        hashes = [("Age.csv", "ed2b9c761dc949708cd6254e6207ff83"),
                  ("Heart Disease.csv", "90f2dede871c545dd1492aef8ed84645"),
                  ("Heart Failure.csv", "2152a8187ff53e9c4224e3c9891b5b33"),
                  ("Report1.md", "a5a88e07280719d99fa8a9bda087cfe7")]

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
