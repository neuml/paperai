"""
Report module tests
"""

import unittest

# pylint: disable=E0401
from paperai.report.execute import Execute

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

        hashes = [("Age.csv", "841aa2fae519f93194ff3f504fa8077a"),
                  ("Heart Disease.csv", "81f09414bb7cfcbd7eedd44e3e612e9c"),
                  ("Heart Failure.csv", "7237afb2784bd4f7850c8ad7c9f7ff88"),
                  ("Report1.md", "69cbf92ca92c45ef78d519aed2e59ca1")]

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

        hashes = [("Match.csv", "3238acd2d7975275665901519030f828"),
                  ("MatchSurround.csv", "fde1f069b6e443d8dfe48a753116e6b8"),
                  ("Section.csv", "30770f6b5ba27334a373a41c8ed6ab0f"),
                  ("Surround.csv", "c14ef9347f983a3d54a5a0e653572e3a"),
                  ("Report2.md", "9218fe80fe5e9fdd50c5719f54c52061")]

        # Check file hashes
        for name, value in hashes:
            self.assertEqual(Utils.hashfile(Utils.PATH + "/" + name), value)
