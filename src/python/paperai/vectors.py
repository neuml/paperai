"""
Vectors module
"""

import os
import os.path
import sqlite3
import sys
import tempfile

from txtai.vectors import WordVectors
from txtai.tokenizer import Tokenizer

from .models import Models

class RowIterator(object):
    """
    Iterates over rows in a database query. Allows for multiple iterations.
    """

    def __init__(self, dbfile):
        """
        Initializes RowIterator.

        Args:
            dbfile: path to SQLite file
        """

        # Store database file
        self.dbfile = dbfile

        self.rows = self.stream(self.dbfile)

    def __iter__(self):
        """
        Creates a database query generator.

        Returns:
            generator
        """

        # reset the generator
        self.rows = self.stream(self.dbfile)
        return self

    def __next__(self):
        """
        Gets the next result in the current generator.

        Returns:
            tokens
        """

        result = next(self.rows)
        if result is None:
            raise StopIteration
        else:
            return result

    def stream(self, dbfile):
        """
        Connects to SQLite file at dbfile and yields parsed tokens for each row.

        Args:
            dbfile:
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        cur.execute("SELECT Text FROM sections")

        count = 0
        for section in cur:
            # Tokenize text
            tokens = Tokenizer.tokenize(section[0])

            count += 1
            if count % 1000 == 0:
                print("Streamed %d documents" % (count), end="\r")

            # Skip documents with no tokens parsed
            if tokens:
                yield tokens

        print("Iterated over %d total rows" % (count))

        # Free database resources
        db.close()

class Vectors(object):
    """
    Methods to build a FastText model.
    """

    @staticmethod
    def tokens(dbfile):
        """
        Iterates over each row in dbfile and writes parsed tokens to a temporary file for processing.

        Args:
            dbfile: SQLite file to read

        Returns:
            path to output file
        """

        tokens = None

        # Stream tokens to temp working file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as output:
            # Save file path
            tokens = output.name

            for row in RowIterator(dbfile):
                output.write(" ".join(row) + "\n")

        return tokens

    @staticmethod
    def run(path, size, mincount, output):
        """
        Builds a word vector model.

        Args:
            path: model path, if None uses default path
            size: dimensions for fastText model
            mincount: minimum number of times a token must appear in input
            output: output file path, if None uses default path
        """

        # Default path if not provided
        if not path:
            path = Models.modelPath()

        # Derive path to dbfile
        dbfile = os.path.join(path, "articles.sqlite")

        # Stream tokens to temporary file
        tokens = Vectors.tokens(dbfile)

        if not output:
            # Output file path
            output = Models.vectorPath("cord19-%dd" % size, True)

        # Build word vectors model
        WordVectors.build(tokens, size, mincount, output)

        # Remove temporary tokens file
        os.remove(tokens)

if __name__ == "__main__":
    # Create vector model
    Vectors.run(sys.argv[1] if len(sys.argv) > 1 else None, 300, 4,
                sys.argv[2] if len(sys.argv) > 2 else None)
