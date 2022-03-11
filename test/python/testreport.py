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
            ("Age.csv", "34448eab17f2a127714fc42ba4baaa78"),
            ("Heart Disease.csv", "96b144fc1566e2c0aa774d098e203922"),
            ("Heart Failure.csv", "afd812f7875c4fcb45bf800952327dba"),
            ("Report1.md", "d3d4682f35662dd1e3665e816e5529ec"),
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
            ("Match.csv", "9cb5ce8896355d049084d61fae13d97f"),
            ("MatchSurround.csv", "47e4d2ec7ae8fda30a78d628d124f204"),
            ("Section.csv", "7113d5af95542193fc3dc21dc785b014"),
            ("Surround.csv", "14d124f85c140077d58ae3636ba8557f"),
            ("Report2.md", "7813d253d7a792f93915c2dccfb78483"),
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
            ("AI.csv", "94f0bead413eb71835c3f27881b29c91"),
            ("All.csv", "3bca7a39a541fa68b3ef457625fb0120"),
            ("Report3.md", "0fc53703dace57e3403294fb8ea7e9d1"),
        ]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)
