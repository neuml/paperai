"""
Utils module
"""

import hashlib

class Utils(object):
    """
    Utility constants and methods
    """

    PATH = "/tmp/paperai"
    DBFILE = PATH + "/articles.sqlite"
    VECTORFILE = PATH + "/vectors.magnitude"

    @staticmethod
    def hashfile(path):
        """
        Builds a MD5 hash for file at path.

        Args:
            path: full path to file

        Returns:
            MD5 hash
        """

        with open(path, "r") as data:
            # Read file into string and build MD5 hash
            return hashlib.md5(data.read().encode()).hexdigest()
