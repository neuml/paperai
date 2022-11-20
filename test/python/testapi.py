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

from paperai.index import Index

# pylint: disable=C0411
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
    @patch.dict(
        os.environ,
        {
            "CONFIG": os.path.join(tempfile.gettempdir(), "testapi.yml"),
            "API_CLASS": "paperai.api.API",
        },
    )
    def start():
        """
        Starts a mock FastAPI client.
        """

        config = os.path.join(tempfile.gettempdir(), "testapi.yml")

        with open(config, "w", encoding="utf-8") as output:
            output.write(INDEX % Utils.PATH)

        client = TestClient(app)
        start()

        return client

    def testSearch(self):
        """
        Test search via API
        """

        # Build embeddings index
        Index.run(
            Utils.PATH,
            {
                "path": Utils.VECTORFILE,
                "scoring": "bm25",
                "pca": 3,
                "faiss": {"nprobe": 6, "components": "IVF100,Flat"},
            },
        )

        # Connect to test instance
        client = TestAPI.start()

        # Run search
        params = urllib.parse.urlencode({"query": "+hypertension ci", "limit": 1})
        results = client.get(f"search?{params}").json()

        # Check number of results
        self.assertEqual(len(results), 1)
