"""
Query module tests
"""

import os
import unittest

from contextlib import redirect_stdout

# pylint: disable=E0401
from paperai.query import Query

from utils import Utils

class TestQuery(unittest.TestCase):
    """
    Query tests
    """

    @unittest.skipIf(os.name == "nt", "Faiss not installed on Windows")
    def testRun(self):
        """
        Test query execution
        """

        # Execute query
        with open(Utils.PATH + "/query.txt", "w", newline="\n") as query:
            with redirect_stdout(query):
                Query.run("risk factors studied", 10, Utils.PATH)

        self.assertEqual(Utils.hashfile(Utils.PATH + "/query.txt"), "b1932b9ceb6c2ea2b626ebb44d89340b")
