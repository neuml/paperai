"""
Shell module tests
"""

import contextlib
import io
import unittest

# pylint: disable=E0401
from paperai.shell import Shell

from utils import Utils

class TestShell(unittest.TestCase):
    """
    Shell tests
    """

    def testShell(self):
        """
        Tests shell action
        """

        shell = Shell(Utils.PATH)
        shell.preloop()

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            shell.default("+hypertension ci")
        shell.postloop()

        self.assertTrue("1.28 (1.06 to 1.53) P-value 0.009" in output.getvalue())
