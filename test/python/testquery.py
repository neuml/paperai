"""
Query module tests
"""

import unittest

from contextlib import redirect_stdout

from paperai.query import Query

# pylint: disable=C0411
from utils import Utils


class TestQuery(unittest.TestCase):
    """
    Query tests
    """

    def testEmpty(self):
        """
        Test empty fields.
        """

        self.assertEqual(Query.authors(None), None)
        self.assertEqual(Query.date(None), None)

    def testDateFormats(self):
        """
        Test multiple date string formats.
        """

        self.assertEqual(Query.date("2024-01-01 00:00:00"), "2024")
        self.assertEqual(Query.date("2024-05-02"), "2024-05-02")
        self.assertEqual(Query.date("2024-05-02T13:45:21Z"), "2024-05-02")
        self.assertEqual(Query.date("not-a-date"), "not-a-date")

    def testRun(self):
        """
        Test query execution
        """

        # Execute query
        with open(Utils.PATH + "/query.txt", "w", newline="\n", encoding="utf-8") as query:
            with redirect_stdout(query):
                Query.run("risk factors studied", 10, Utils.PATH)

        self.assertEqual(Utils.linecount(Utils.PATH + "/query.txt"), 106)
