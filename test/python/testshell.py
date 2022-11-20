"""
Shell module tests
"""

import contextlib
import io
import unittest

from paperai.shell import Shell

# pylint: disable=C0411
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

        self.assertTrue("hypertension" in output.getvalue())
