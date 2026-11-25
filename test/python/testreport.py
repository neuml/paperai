"""
Report module tests
"""

import unittest
from unittest.mock import Mock, patch

from paperai.report.common import Report
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

    @patch("paperai.report.common.RAG", autospec=True)
    @patch("paperai.report.common.Labels")
    @patch("paperai.report.common.Similarity")
    def testModelOptions(self, similarity, _labels, rag):
        """
        Test report model selection and forwarding of RAG options
        """

        embeddings = Mock()
        for options, model in [
            ({}, "NeuML/bert-small-cord19qa"),
            ({"qa": "custom-qa"}, "custom-qa"),
            ({"qa": "custom-qa", "llm": "custom-llm"}, "custom-llm"),
            ({"similarity": "custom-retriever", "qa": "custom-qa"}, "custom-qa"),
        ]:
            with self.subTest(options=options):
                Report(embeddings, Mock(), {**options, "context": 7})
                retriever = similarity.return_value if "similarity" in options else embeddings
                rag.assert_called_with(retriever, model, context=7)

    def testReport1(self):
        """
        Runs test queries from report1.yml test file
        """

        # Execute report
        Execute.run(Utils.PATH + "/report1.yml", 10, "csv", Utils.PATH, None)
        Execute.run(Utils.PATH + "/report1.yml", 10, "md", Utils.PATH, None)

        counts = [
            ("Age.csv", 11),
            ("Heart Disease.csv", 5),
            ("Heart Failure.csv", 7),
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
