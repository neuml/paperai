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
            ("Age.csv", "6a0c4326e5c3136ad1c46606e04e9f62"),
            ("Heart Disease.csv", "96b144fc1566e2c0aa774d098e203922"),
            ("Heart Failure.csv", "2e8da24e09b46f71870af9ce146ade76"),
            ("Report1.md", "3dadaf334251d8d9b8354cd7142c5ec9"),
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
            ("Match.csv", "c48e3205aac18e94bac915c9dbaacc89"),
            ("MatchSurround.csv", "df53a94064c138907d9dee9c3029c542"),
            ("Section.csv", "e3745af5f23041f5e68bdffa8abb2e56"),
            ("Surround.csv", "96814dd27a62c28e226cc7505fee9d80"),
            ("Report2.md", "45c37f77cdfe8e4f213d8b3b18726cee"),
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
