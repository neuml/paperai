"""
Models module
"""

import os
import os.path
import sqlite3

from txtai.embeddings import Embeddings


class Models:
    """
    Common methods for generating data paths.
    """

    @staticmethod
    def load(path):
        """
        Loads an embeddings model and db database.

        Args:
            path: model path

        Returns:
            (embeddings, db handle)
        """

        dbfile = os.path.join(path, "articles.sqlite")

        if os.path.isfile(os.path.join(path, "config")):
            print(f"Loading model from {path}")
            embeddings = Embeddings()
            embeddings.load(path)
        else:
            embeddings = None

        # Connect to database file
        db = sqlite3.connect(dbfile)

        return (embeddings, db)

    @staticmethod
    def close(db):
        """
        Closes a SQLite database database.

        Args:
            db: open database
        """

        # Free database resources
        db.close()
