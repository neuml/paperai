"""
Markdown report module
"""

from ..query import Query

from .common import Report

class Markdown(Report):
    """
    Report writer for Markdown.
    """

    def encode(self, url):
        """
        URL encodes parens as they cause issues with markdown links.

        Args:
            url: input url

        Returns:
            url with parens encoded
        """

        # Escape ()
        return url.replace("(", "%28").replace(")", "%29") if url else url

    def column(self, value):
        """
        Escapes invalid characters (| char) within a table column value.

        Args:
            value: input value

        Returns:
            value with | escaped
        """

        # Escape |
        return value.replace("|", "&#124;") if value else value

    def write(self, output, line):
        """
        Writes line to output file.

        Args:
            output: output file
            line: line to write
        """

        output.write("%s\n" % line)

    def query(self, output, task, query):
        self.write(output, "# %s" % query)

    def section(self, output, name):
        self.write(output, "#### %s<br/>" % name)

    def highlight(self, output, article, highlight):
        # Build citation link
        link = "[%s](%s)" % (Query.authors(article[0]) if article[0] else "Source", self.encode(article[1]))

        # Build highlight row with citation link
        self.write(output, "- %s %s<br/>" % (Query.text(highlight), link))

    def headers(self, columns, output):
        self.names = columns

        # Remove extended study columns
        for field in ["Journal", "Study Link", "Sample Text"]:
            if field in self.names:
                self.names.remove(field)

        # Write table header
        headers = "|".join(self.names)
        self.write(output, "|%s|" % headers)

        # Write markdown separator for headers
        headers = "|".join(["----"] * len(self.names))
        self.write(output, "|%s|" % headers)

    def buildRow(self, article, sections, calculated):
        row = {}

        # Date
        row["Date"] = Query.date(article[0]) if article[0] else ""

        # Title
        title = "[%s](%s)" % (article[1], self.encode(article[2]))

        # Append Publication if available. Assume preprint otherwise and show preprint source.
        title += "<br/>%s" % (article[3] if article[3] else article[4])

        # Source
        row["Source"] = article[4]

        # Title + Publication if available
        row["Study"] = title

        # Study Type
        row["Study Type"] = Query.design(article[5])

        # Sample Size
        sample = Query.sample(article[6], article[7])
        row["Sample Size"] = sample if sample else ""

        # Study Population
        row["Study Population"] = Query.text(article[8]) if article[8] else ""

        # Top Matches
        row["Matches"] = "<br/><br/>".join([Query.text(text) for _, text in sections]) if sections else ""

        # Entry Date
        row["Entry"] = article[9] if article[9] else ""

        # Merge in calculated fields
        row.update(calculated)

        # Escape | characters embedded within columns
        return {column: self.column(row[column]) for column in row}

    def writeRow(self, output, row):
        self.write(output, "|%s|" % "|".join(row))

    def separator(self, output):
        # Write section separator
        self.write(output, "")
