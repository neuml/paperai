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

    def __init__(self, embeddings, db, qa):
        super(CSV, self).__init__(embeddings, db, qa)

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

        self.csvout = open(os.path.join(os.path.dirname(output.name), "%s.csv" % task), "w", newline="")
        self.writer = csv.writer(self.csvout, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

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
        columns = {}

        # Date
        columns["Date"] = Query.date(article[0]) if article[0] else ""

        # Study
        columns["Study"] = article[1]

        # Study Link
        columns["Study Link"] = article[2]

        # Journal
        columns["Journal"] = article[3] if article[3] else article[4]

        # Source
        columns["Source"] = article[4]

        # Study Type
        columns["Study Type"] = Query.design(article[5])

        # Sample Size
        columns["Sample Size"] = article[6]

        # Study Population
        columns["Study Population"] = Query.text(article[8] if article[8] else article[7])

        # Sample Text
        columns["Sample Text"] = article[7]

        # Top Matches
        columns["Matches"] = "\n\n".join([Query.text(text) for _, text in sections]) if sections else ""

        # Entry Date
        columns["Entry"] = article[9] if article[9] else ""

        # Merge in calculated fields
        columns.update(calculated)

        return columns

    def writeRow(self, output, row):
        self.write(row)
