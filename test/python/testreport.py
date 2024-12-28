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

    def testInvalid(self):
        """
        Test invalid parameters
        """

        with self.assertRaises(ValueError):
            Execute.run(Utils.PATH + "/report1.yml", 10, "invalid", Utils.PATH, None)

    def testReport1(self):
        """
        Runs test queries from report1.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report1.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report1.yml", 10, "md", Utils.PATH, None)

        counts = [
            ("Age.csv", 31),
            ("Heart Disease.csv", 7),
            ("Heart Failure.csv", 9),
            ("Report1.md", 47),
        ]

        # Check line counts
        for name, value in counts:
            self.assertEqual(Utils.linecount(Utils.PATH + "/" + name), value)

    def testReport2(self):
        """
        Runs test queries from report2.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report2.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report2.yml", 10, "md", Utils.PATH, None)

        counts = [
            ("Match.csv", 11),
            ("MatchSurround.csv", 11),
            ("Section.csv", 11),
            ("Surround.csv", 11),
            ("Report2.md", 76),
        ]

        # Check line counts
        for name, value in counts:
            self.assertEqual(Utils.linecount(Utils.PATH + "/" + name), value)

    def testReport3(self):
        """
        Runs test queries from report3.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report3.yml", 1, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "md", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report3.yml", 1, "ant", Utils.PATH, None, Utils.PATH)

        counts = [
            ("AI.csv", 2),
            ("All.csv", 501),
            ("Report3.md", 517),
        ]

        # Check line counts
        for name, value in counts:
            self.assertEqual(Utils.linecount(Utils.PATH + "/" + name), value)
