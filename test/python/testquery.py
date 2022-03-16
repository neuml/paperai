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

    def testRun(self):
        """
        Test query execution
        """

        # Execute query
        with open(
            Utils.PATH + "/query.txt", "w", newline="\n", encoding="utf-8"
        ) as query:
            with redirect_stdout(query):
                Query.run("risk factors studied", 10, Utils.PATH)

        with open(Utils.PATH + "/query.txt", "r", encoding="utf-8") as f:
            print(f.read())

        self.assertEqual(
            Utils.hashfile(Utils.PATH + "/query.txt"),
            "c81b87b34b7efec05b79e61de319e6df",
        )
