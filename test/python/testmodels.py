"""
Models module tests
"""

import unittest

# pylint: disable=E0401
from paperai.models import Models

class TestModels(unittest.TestCase):
    """
    Models tests
    """

    def testBasePath(self):
        """
        Test base path
        """

        self.assertTrue(Models.basePath().endswith(".cord19"))

    def testModelPath(self):
        """
        Test model path
        """

        self.assertTrue(Models.modelPath().endswith("models"))

    def testVectorPath(self):
        """
        Test vector path
        """

        self.assertTrue(Models.vectorPath("test").endswith("test"))
 