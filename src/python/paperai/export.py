"""
Export module
"""

import os
import os.path
import sqlite3
import sys

import regex as re

# pylint: disable=E0611
# Defined at runtime
from .index import Index
from .models import Models

class Export(object):
    """
    Exports database rows into a text file line-by-line.
    """

    @staticmethod
    def stream(dbfile, output):
        """
        Iterates over each row in dbfile and writes text to output file

        Args:
            dbfile: SQLite file to read
            output: output file to store text
        """

        with open(output, "w") as output:
            # Connection to database file
            db = sqlite3.connect(dbfile)
            cur = db.cursor()

            # Get all indexed text, with a detected study design, excluding modeling designs
            cur.execute(Index.SECTION_QUERY + " AND design NOT IN (0, 9)")

            count = 0
            for _, name, text in cur:
                if not name or not re.search(Index.SECTION_FILTER, name.lower()):
                    count += 1
                    if count % 1000 == 0:
                        print("Streamed %d documents" % (count), end="\r")

                    # Write row
                    if text:
                        output.write(text + "\n")

            print("Iterated over %d total rows" % (count))

            # Free database resources
            db.close()

    @staticmethod
    def run(output, path):
        """
        Exports data from database to text file, line by line.

        Args:
            output: output file path
            path: model path, if None uses default path
        """

        # Default path if not provided
        if not path:
            path = Models.modelPath()

        # Derive path to dbfile
        dbfile = os.path.join(path, "articles.sqlite")

        # Stream text from database to file
        Export.stream(dbfile, output)

if __name__ == "__main__":
    # Export data
    Export.run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
