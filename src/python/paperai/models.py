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
    def basePath(create=False):
        """
        Base data path - ~/.cord19

        Args:
            create: if directory should be created

        Returns:
            path
        """

        # Get model cache path
        path = os.path.join(os.path.expanduser("~"), ".cord19")

        # Create directory if required
        if create:
            os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def modelPath(create=False):
        """
        Model path for name

        Args:
            create: if directory should be created

        Returns:
            path
        """

        path = os.path.join(Models.basePath(), "models")

        # Create directory if required
        if create:
            os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def vectorPath(name, create=False):
        """
        Vector path for name

        Args:
            name: vectors name
            create: if directory should be created

        Returns:
            path
        """

        path = os.path.join(Models.basePath(), "vectors")

        # Create directory path if required
        if create:
            os.makedirs(path, exist_ok=True)

        # Append file name to path
        return os.path.join(path, name)

    @staticmethod
    def load(path):
        """
        Loads an embeddings model and db database.

        Args:
            path: model path, if None uses default path

        Returns:
            (embeddings, db handle)
        """

        # Default path if not provided
        if not path:
            path = Models.modelPath()

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
