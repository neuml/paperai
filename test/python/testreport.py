"""
Report module tests
"""

import unittest

from paperai.report.execute import Execute

# pylint: disable=C0411
from utils import Utils


class TestReport(unittest.TestCase):
    """
    Report tests
    """

    def testReport1(self):
        """
        Runs test queries from report1.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report1.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report1.yml", 10, "md", Utils.PATH, None)

        hashes = [
            ("Age.csv", "237c2d024f758139833d681c0f7828aa"),
            ("Heart Disease.csv", "542003f5677b35b73e0b3fff07398789"),
            ("Heart Failure.csv", "a29c59d63d73c225102d74977efeac34"),
            ("Report1.md", "6b143c03c154cef1c6d38e0ac1a2eee9"),
        ]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)

    def testReport2(self):
        """
        Runs test queries from report2.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report2.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report2.yml", 10, "md", Utils.PATH, None)

        hashes = [
            ("Match.csv", "4b186a90a7bc9aa7e9f65608acac3235"),
            ("MatchSurround.csv", "4eae0e75b75f7b7b158094de217362a5"),
            ("Section.csv", "32e6c53fc7c87595846e00db4fe4b1b8"),
            ("Surround.csv", "aa2add9eaf4a2e1b2b48753c2172772c"),
            ("Report2.md", "6133aa0ebcfa5a363e0e187daba8c1de"),
        ]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)

    def testReport3(self):
        """
        Runs test queries from report3.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report3.yml", 1, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "md", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "ant", Utils.PATH, None, Utils.PATH)

        hashes = [
            ("AI.csv", "858bfb2c0026de725cb06417e639237a"),
            ("All.csv", "3bca7a39a541fa68b3ef457625fb0120"),
            ("Report3.md", "c4cf822444643effbb502baaf44d993c"),
        ]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)
