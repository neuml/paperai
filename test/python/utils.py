"""
Utils module
"""


class Utils:
    """
    Utility constants and methods
    """

    PATH = "/tmp/paperai"
    DBFILE = PATH + "/articles.sqlite"
    VECTORFILE = PATH + "/vectors.magnitude"

    @staticmethod
    def linecount(path):
        """
        Counts the number of lines for file at path.

        Args:
            path: full path to file

        Returns:
            number of lines
        """

        with open(path, "r", encoding="utf-8") as f:
            return len(f.readlines())
