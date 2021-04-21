"""
API module tests
"""

import os
import tempfile
import unittest
import urllib

from unittest.mock import patch

from fastapi.testclient import TestClient

from txtai.api import app, start

# pylint: disable=E0401
from paperai.index import Index

from utils import Utils

# Configuration for a paperai index
INDEX = """
embeddings:
path: %s
"""

class TestAPI(unittest.TestCase):
    """
    API tests
    """

    @staticmethod
    @patch.dict(os.environ, {"CONFIG": os.path.join(tempfile.gettempdir(), "testapi.yml"), "API_CLASS": "paperai.api.API"})
    def start():
        """
        Starts a mock FastAPI client.
        """

        config = os.path.join(tempfile.gettempdir(), "testapi.yml")

        with open(config, "w") as output:
            output.write(INDEX % Utils.PATH)

        client = TestClient(app)
        start()

        return client

    def testSearch(self):
        """
        Test search via API
        """

        # Build embeddings index
        Index.run(Utils.PATH, Utils.VECTORFILE)

        # Connect to test instance
        client = TestAPI.start()

        # Run search
        params = urllib.parse.urlencode({"query": "+hypertension ci", "limit": 1})
        results= client.get("search?%s" % params).json()

        # Check number of results
        self.assertEqual(len(results), 1)
