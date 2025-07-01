"""
Indexing module
"""

import os.path
import sqlite3
import sys

import regex as re
import yaml

from txtai.embeddings import Embeddings
from txtai.pipeline import Tokenizer
from txtai.vectors import WordVectors


class Index:
    """
    Methods to build a new vector embeddings index.
    """

    # Section query and filtering logic constants
    SECTION_FILTER = r"background|(?<!.*?results.*?)discussion|introduction|reference"
    SECTION_QUERY = "SELECT Id, Name, Text FROM sections"

    @staticmethod
    def stream(dbfile, maxsize, toprank, scoring):
        """
        Streams documents from an articles.sqlite file. This method is a generator and will yield a row at time.

        Args:
            dbfile: input SQLite file
            maxsize: maximum number of documents to process
            toprank: only index the topn ranked articles by citation count within the dataset
            scoring: True if index uses a scoring model, False otherwise
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        # Select sections from tagged articles
        query = Index.SECTION_QUERY + " WHERE article in (SELECT article FROM articles a WHERE a.id = article AND a.tags IS NOT NULL)"

        if maxsize > 0:
            query += f" AND article in (SELECT id FROM articles ORDER BY entry DESC LIMIT {maxsize})"

        if toprank > 0:
            query += f" AND article in (SELECT reference FROM citations GROUP BY reference ORDER BY count(*) DESC LIMIT {toprank})"

        # Run the query
        cur.execute(query)

        count = 0
        for row in cur:
            # Unpack row
            uid, name, text = row

            if not scoring or not name or not re.search(Index.SECTION_FILTER, name.lower()):
                # Tokenize text
                text = Tokenizer.tokenize(text) if scoring else text

                document = (uid, text, None)

                count += 1
                if count % 1000 == 0:
                    print(f"Streamed {count} documents", end="\r")

                # Skip documents with no tokens parsed
                if text:
                    yield document

        print(f"Iterated over {count} total rows")

        # Free database resources
        db.close()

    @staticmethod
    def config(vectors):
        """
        Builds embeddings configuration.

        Args:
            vectors: vector model path or configuration

        Returns:
            configuration
        """

        # Configuration as a dictionary
        if isinstance(vectors, dict):
            return vectors

        # Configuration as a YAML file
        if isinstance(vectors, str) and vectors.endswith(".yml"):
            with open(vectors, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        # Configuration for word vectors model
        if WordVectors.isdatabase(vectors):
            return {"path": vectors, "scoring": "bm25", "pca": 3, "quantize": True}

        # Use vector path if provided, else use default txtai configuration
        return {"path": vectors} if vectors else None

    @staticmethod
    def embeddings(dbfile, vectors, maxsize, toprank):
        """
        Builds a vector embeddings index.

        Args:
            dbfile: input SQLite file
            vectors: path to vectors file or configuration
            maxsize: maximum number of documents to process
            toprank: only index the topn ranked articles by citation count within the dataset

        Returns:
            embeddings index
        """

        # Read config and create Embeddings instance
        embeddings = Embeddings(Index.config(vectors))
        scoring = embeddings.isweighted()

        # Build scoring index if scoring method provided
        if scoring:
            embeddings.score(Index.stream(dbfile, maxsize, toprank, scoring))

        # Build embeddings index
        embeddings.index(Index.stream(dbfile, maxsize, toprank, scoring))

        return embeddings

    @staticmethod
    def run(path, vectors, maxsize=0, toprank=0):
        """
        Executes an index run.

        Args:
            path: model path
            vectors: path to vectors file or configuration, if None uses default path
            maxsize: maximum number of documents to process
            toprank: only index the topn ranked articles by citation count within the dataset
        """

        dbfile = os.path.join(path, "articles.sqlite")

        print("Building new model")
        embeddings = Index.embeddings(dbfile, vectors, maxsize, toprank)
        embeddings.save(path)


if __name__ == "__main__":
    Index.run(
        sys.argv[1] if len(sys.argv) > 1 else None,
        sys.argv[2] if len(sys.argv) > 2 else None,
        int(sys.argv[3]) if len(sys.argv) > 3 else 0,
        int(sys.argv[4]) if len(sys.argv) > 4 else 0,
    )
