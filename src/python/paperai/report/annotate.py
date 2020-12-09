"""
Annotate report module
"""

import os
import os.path
import re

from txtmarker.factory import Factory

from ..query import Query

from .common import Report

class Annotate(Report):
    """
    Report writer for overlaying annotations on source PDFs. This format requires access to original PDFs.
    """

    def __init__(self, embeddings, db, qa, indir):
        """
        Creates a new report.

        Args:
            embeddings: embeddings index
            db: database connection
            qa: qa model path
            indir: path to input directory containing source files
        """

        super(Annotate, self).__init__(embeddings, db, qa)

        # List of all source files
        self.files = []

        # Recursively walk directory and store file paths
        for root, _, files in sorted(os.walk(indir)):
            for f in sorted(files):
                self.files.append(os.path.join(root, f))

    def cleanup(self, outfile):
        # Delete created master csv file
        os.remove(outfile)

    def headers(self, columns, output):
        self.names = columns

        # Do not annotate following columns
        for field in ["Date", "Study", "Study Link", "Journal", "Study Type", "Sample Size", "Matches", "Entry"]:
            if field in self.names:
                self.names.remove(field)

        # Always store source as it's needed for annotation
        if "Source" not in self.names:
            self.names.append("Source")

    def buildRow(self, article, sections, calculated):
        row = {}

        # Date - required report field
        row["Date"] = Query.date(article[0]) if article[0] else ""

        # Source
        row["Source"] = article[4]

        # Sample Text
        row["Sample Text"] = article[7]

        # Study Population
        row["Study Population"] = Query.text(article[8] if article[8] else article[7])

        # Merge in calculated fields
        row.update(calculated)

        return row

    def writeRow(self, output, row):
        # Create output directory path
        output = os.path.dirname(output.name)

        # Create annotated source file
        self.annotate(output, row)

    def annotate(self, output, row):
        """
        Annotates source pdf using data in row.

        Args:
            source: source file name
            row: row with column values to provide annotations
        """

        # Combine header and values tuple into dict
        row = dict(zip(self.names, row))

        # Get source
        source = row.pop("Source")

        # Create highlighter instance
        highlighter = Factory.create("pdf", self.formatter, 4)

        # Find matching source file in input files list
        match = [f for f in self.files if os.path.basename(f) == source]
        if match:
            highlights = []

            # Create annotation for each component in result column
            for name, value in sorted(row.items()):
                if value:
                    # Only annotate best match
                    text = value.split("\n\n")[0]

                    highlights.append((name, text))

            # Generate output directory
            output = os.path.join(output, "annotations")
            os.makedirs(output, exist_ok=True)

            # Output file path
            output = os.path.join(output, source)

            # Annotate file
            highlighter.highlight(match[0], output, highlights)

    def formatter(self, text):
        """
        Custom formatter that is passed to PDF Annotation method. This logic maps data cleansing logic in paperetl.

        Reference: https://github.com/neuml/paperetl/blob/master/src/python/paperetl/text.py

        Args:
            text: input text

        Returns:
            clean text
        """

        # List of patterns
        patterns = []

        # Remove emails
        patterns.append(r"\w+@\w+(\.[a-z]{2,})+")

        # Remove urls
        patterns.append(r"http(s)?\:\/\/\S+")

        # Remove single characters repeated at least 3 times (ex. j o u r n a l)
        patterns.append(r"(^|\s)(\w\s+){3,}")

        # Remove citations references (ex. [3] [4] [5])
        patterns.append(r"(\[\d+\]\,?\s?){3,}(\.|\,)?")

        # Remove citations references (ex. [3, 4, 5])
        patterns.append(r"\[[\d\,\s]+\]")

        # Remove citations references (ex. (NUM1) repeated at least 3 times with whitespace
        patterns.append(r"(\(\d+\)\s){3,}")

        # Build regex pattern
        pattern = re.compile("|".join(["(%s)" % p for p in patterns]))

        text = pattern.sub(" ", text)

        # Clean/transform text
        text = pattern.sub(" ", text)

        # Remove extra spacing either caused by replacements or already in text
        text = re.sub(r" {2,}|\.{2,}", " ", text)

        # Limit to alphanumeric characters
        text = re.sub(r"[^A-Za-z0-9]", "", text)

        return text
