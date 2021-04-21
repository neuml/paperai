"""
API module tests
"""

import hashlib
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

    @classmethod
    def setUpClass(cls):
        """
        Create API client on creation of class.
        """

        # Build embeddings index
        Index.run(Utils.PATH, Utils.VECTORFILE)

        cls.client = TestAPI.start()

    def testSearch(self):
        """
        Test search via API
        """

        params = urllib.parse.urlencode({"query": "+hypertension ci", "limit": 1})

        values = ["%s%s" % (k, v) for k, v in sorted(self.client.get("search?%s" % params).json()[0].items())]
        md5 = hashlib.md5(" ".join(values).encode()).hexdigest()

        self.assertEqual(md5, "07ee525ff2b50142c88fb50afcf46582")
