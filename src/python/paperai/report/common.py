"""
Report module
"""

import regex as re

from txtai.extractor import Extractor

from ..index import Index
from ..query import Query

class Report(object):
    """
    Methods to build reports from a series of queries
    """

    def __init__(self, embeddings, db, qa):
        """
        Creates a new report.

        Args:
            embeddings: embeddings index
            db: database connection
            qa: qa model path
        """

        # Store references to embeddings index and open database cursor
        self.embeddings = embeddings
        self.cur = db.cursor()

        # Column names
        self.names = []

        # Extractive question-answering model
        self.extractor = Extractor(self.embeddings, qa if qa else "NeuML/bert-small-cord19qa", False)

    def build(self, queries, topn, output):
        """
        Builds a report using a list of input queries

        Args:
            queries: queries to execute
            topn: number of documents to return
            output: output I/O object
        """

        # Default to 50 documents if not specified
        topn = topn if topn else 50

        for name, config in queries:
            query = config["query"]
            columns = config["columns"]

            # Write query string
            self.query(output, name, query)

            # Write separator
            self.separator(output)

            # Query for best matches
            results = Query.search(self.embeddings, self.cur, query, topn)

            # Generate highlights section
            self.section(output, "Highlights")

            # Generate highlights
            self.highlights(output, results, int(topn / 10))

            # Separator between highlights and articles
            self.separator(output)

            # Generate articles section
            self.section(output, "Articles")

            # Generate table headers
            self.headers([column["name"] for column in columns], output)

            # Generate table rows
            self.articles(output, topn, (name, query, columns), results)

            # Write section separator
            self.separator(output)

    def highlights(self, output, results, topn):
        """
        Builds a highlights section.

        Args:
            output: output file
            results: search results
            topn: number of results to return
        """

        # Extract top sections as highlights
        for highlight in Query.highlights(results, topn):
            # Get matching article
            uid = [article for _, _, article, text in results if text == highlight][0]
            self.cur.execute("SELECT Authors, Reference FROM articles WHERE id = ?", [uid])
            article = self.cur.fetchone()

            # Write out highlight row
            self.highlight(output, article, highlight)

    def articles(self, output, topn, metadata, results):
        """
        Builds an articles section.

        Args:
            output: output file
            topn: number of documents to return
            metadata: query metadata
            results: search results
        """

        # Unpack metadata
        _, query, _ = metadata

        # Retrieve list of documents
        documents = Query.all(self.cur) if query == "*" else Query.documents(results, topn)

        # Collect matching rows
        rows = []

        for uid in documents:
            # Get article metadata
            self.cur.execute("SELECT Published, Title, Reference, Publication, Source, Design, Size, Sample, Method, Entry " +
                             "FROM articles WHERE id = ?", [uid])
            article = self.cur.fetchone()

            # Calculate derived fields
            calculated = self.calculate(uid, metadata)

            # Builds a row for article
            rows.append(self.buildRow(article, documents[uid], calculated))

        # Print report by published desc
        for row in sorted(rows, key=lambda x: x["Date"], reverse=True):
            # Convert row dict to list
            row = [row[column] for column in self.names]

            # Write out row
            self.writeRow(output, row)

    def calculate(self, uid, metadata):
        """
        Builds a dict of calculated fields for a given document.

        Args:
            uid: document id
            metadata: query metadata

        Returns:
            {name: value} containing derived column values
        """

        fields = {}
        questions = []

        # Unpack metadata
        _, _, columns = metadata

        for column in columns:
            # Constant column
            if "constant" in column:
                fields[column["name"]] = column["constant"]
            # Question-answer column
            elif "query" in column:
                # Query variable substitutions
                query = self.variables(column["query"], metadata)
                question = self.variables(column["question"], metadata) if "question" in column else query
                snippet = column["snippet"] if "snippet" in column else False

                questions.append((column["name"], query, question, snippet))

        # Retrieve indexed document text for article
        self.cur.execute(Index.SECTION_QUERY + " AND article = ?", [uid])

        # Get list of document text sections
        sections = []
        for sid, name, text in self.cur.fetchall():
            if not name or not re.search(Index.SECTION_FILTER, name.lower()):
                sections.append((sid, text))

        # Add extraction fields
        for name, value in self.extractor(sections, questions):
            fields[name] = value if value else ""

        return fields

    def variables(self, value, metadata):
        """
        Runs variable substitution for value.

        Args:
            value: input value
            metadata: query metadata

        Returns:
            value with variable substitution
        """

        name, query, _ = metadata

        # Cleanup name for queries
        name = name.replace("_", "").lower()
        query = query.lower()

        if value:
            value = value.replace("$NAME", name).replace("$QUERY", query)

        return value

    def cleanup(self, outfile):
        """
        Allow freeing or cleaning up resources.

        Args:
            outfile: output file path
        """

    def query(self, output, task, query):
        """
        Writes query.

        Args:
            output: output file
            task: task name
            query: query string
        """

    def section(self, output, name):
        """
        Writes a section name

        Args:
            output: output file
            name: section name
        """

    def highlight(self, output, article, highlight):
        """
        Writes a highlight row

        Args:
            output: output file
            article: article reference
            highlight: highlight text
        """

    def headers(self, columns, output):
        """
        Writes table headers.

        Args:
            columns: column names
            output: output file
        """

    def buildRow(self, article, sections, calculated):
        """
        Converts a document to a table row.

        Args:
            article: article
            sections: text sections for article
            calculated: calculated fields
        """

    def writeRow(self, output, row):
        """
        Writes a table row.

        Args:
            output: output file
            row: output row
        """

    def separator(self, output):
        """
        Writes a separator between sections
        """
