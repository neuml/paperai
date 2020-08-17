"""
Indexing module
"""

import os.path
import sqlite3
import sys

import regex as re

from txtai.embeddings import Embeddings
from txtai.tokenizer import Tokenizer

from .models import Models

class Index(object):
    """
    Methods to build a new sentence embeddings index.
    """

    # Section query and filtering logic constants
    SECTION_FILTER = r"background|(?<!.*?results.*?)discussion|introduction|reference"
    SECTION_QUERY = "SELECT Id, Name, Text FROM sections WHERE (labels is null or labels NOT IN ('FRAGMENT', 'QUESTION'))"

    @staticmethod
    def stream(dbfile):
        """
        Streams documents from an articles.sqlite file. This method is a generator and will yield a row at time.

        Args:
            dbfile: input SQLite file
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        # Select tagged sentences without a NLP label. NLP labels are set for non-informative sentences.
        cur.execute(Index.SECTION_QUERY + " AND tags is not null")

        count = 0
        for row in cur:
            # Unpack row
            uid, name, text = row

            if not name or not re.search(Index.SECTION_FILTER, name.lower()):
                # Tokenize text
                tokens = Tokenizer.tokenize(text)

                document = (uid, tokens, None)

                count += 1
                if count % 1000 == 0:
                    print("Streamed %d documents" % (count), end="\r")

                # Skip documents with no tokens parsed
                if tokens:
                    yield document

        print("Iterated over %d total rows" % (count))

        # Free database resources
        db.close()

    @staticmethod
    def embeddings(dbfile, vectors):
        """
        Builds a sentence embeddings index.

        Args:
            dbfile: input SQLite file
            vectors: vector path

        Returns:
            embeddings index
        """

        embeddings = Embeddings({"path": vectors,
                                 "scoring": "bm25",
                                 "pca": 3,
                                 "quantize": True})

        # Build scoring index if scoring method provided
        if embeddings.config.get("scoring"):
            embeddings.score(Index.stream(dbfile))

        # Build embeddings index
        embeddings.index(Index.stream(dbfile))

        return embeddings

    @staticmethod
    def run(path, vectors):
        """
        Executes an index run.

        Args:
            path: model path, if None uses default path
            vectors: vector path, if None uses default path
        """

        # Default path if not provided
        if not path:
            path = Models.modelPath()

        dbfile = os.path.join(path, "articles.sqlite")

        # Default vectors
        if not vectors:
            vectors = Models.vectorPath("cord19-300d.magnitude")

        print("Building new model")
        embeddings = Index.embeddings(dbfile, vectors)
        embeddings.save(path)

if __name__ == "__main__":
    Index.run(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else None)
