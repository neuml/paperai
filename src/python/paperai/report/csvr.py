"""
CSV report module
"""

import csv
import os
import os.path

from ..query import Query

from .common import Report


class CSV(Report):
    """
    Report writer for CSV exports. Format is designed to be imported into other tools.
    """

    def __init__(self, embeddings, db, options):
        super().__init__(embeddings, db, options)

        # CSV writer handle
        self.csvout = None
        self.writer = None

    def cleanup(self, outfile):
        # Delete created master csv file
        os.remove(outfile)

    def query(self, output, task, query):
        # Close existing file
        if self.csvout:
            self.csvout.close()

        # pylint: disable=R1732
        self.csvout = open(
            os.path.join(os.path.dirname(output.name), f"{task}.csv"),
            "w",
            newline="",
            encoding="utf-8",
        )

        self.writer = csv.writer(
            self.csvout, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

    def write(self, row):
        """
        Writes line to output file.

        Args:
            line: line to write
        """

        # Write csv line
        self.writer.writerow(row)

    def headers(self, columns, output):
        self.names = columns

        # Write out column names
        self.write(self.names)

    def buildRow(self, article, sections, calculated):
        row = {}

        # Date
        row["Date"] = Query.date(article[0]) if article[0] else ""

        # Study
        row["Study"] = article[1]

        # Study Link
        row["Study Link"] = article[2]

        # Journal
        row["Journal"] = article[3] if article[3] else article[4]

        # Source
        row["Source"] = article[4]

        # Top Matches
        row["Matches"] = (
            "\n\n".join([Query.text(text) for _, text in sections]) if sections else ""
        )

        # Entry Date
        row["Entry"] = article[5] if article[5] else ""

        # Id
        row["Id"] = article[6]

        # Merge in calculated fields
        row.update(calculated)

        return row

    def writeRow(self, output, row):
        self.write(row)
