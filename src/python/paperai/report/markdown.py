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

        output.write(f"{line}\n")

    def query(self, output, task, query):
        self.write(output, f"# {query}")

    def section(self, output, name):
        self.write(output, f"#### {name}<br/>")

    def highlight(self, output, article, highlight):
        # Build citation link
        link = f"[{Query.authors(article[0]) if article[0] else 'Source'}]({self.encode(article[1])})"

        # Build highlight row with citation link
        self.write(output, f"- {Query.text(highlight)} {link}<br/>")

    def headers(self, columns, output):
        self.names = columns

        # Remove extended study columns
        for field in ["Journal", "Study Link", "Sample Text"]:
            if field in self.names:
                self.names.remove(field)

        # Write table header
        headers = "|".join(self.names)
        self.write(output, f"|{headers}|")

        # Write markdown separator for headers
        headers = "|".join(["----"] * len(self.names))
        self.write(output, f"|{headers}|")

    def buildRow(self, article, sections, calculated):
        row = {}

        # Date
        row["Date"] = Query.date(article[0]) if article[0] else ""

        # Title
        title = f"[{article[1]}]({self.encode(article[2])})"

        # Append Publication if available. Assume preprint otherwise and show preprint source.
        title += f"<br/>{article[3] if article[3] else article[4]}"

        # Source
        row["Source"] = article[4]

        # Title + Publication if available
        row["Study"] = title

        # Top Matches
        row["Matches"] = "<br/><br/>".join([Query.text(text) for _, text in sections]) if sections else ""

        # Entry Date
        row["Entry"] = article[5] if article[5] else ""

        # Id
        row["Id"] = article[6]

        # Merge in calculated fields
        row.update(calculated)

        # Escape | characters embedded within columns
        return {name: self.column(value) for name, value in row.items()}

    def writeRow(self, output, row):
        self.write(output, f"|{'|'.join(row)}|")

    def separator(self, output):
        # Write section separator
        self.write(output, "")
