"""
Report module
"""

import regex as re

from txtai.pipeline import Labels, RAG, Similarity, Tokenizer

from ..index import Index
from ..query import Query

from .column import Column


class Report:
    """
    Methods to build reports from a series of queries
    """

    def __init__(self, embeddings, db, options):
        """
        Creates a new report.

        Args:
            embeddings: embeddings index
            db: database connection
            options: report options
        """

        # Store references to embeddings index and open database cursor
        self.embeddings = embeddings
        self.cur = db.cursor()

        # Report options
        self.options = options

        # Column names
        self.names = []

        self.similarity = Similarity(options["similarity"]) if "similarity" in options else None
        self.labels = Labels(model=self.similarity) if self.similarity else None

        # Question-answering model
        # Determine if embeddings or a custom similarity model should be used to build question context
        self.rag = RAG(
            self.similarity if self.similarity else self.embeddings,
            options["qa"] if options.get("qa") else "NeuML/bert-small-cord19qa",
            minscore=options.get("minscore"),
            mintokens=options.get("mintokens"),
            context=options.get("context"),
        )

    def build(self, queries, options, output):
        """
        Builds a report using a list of input queries

        Args:
            queries: queries to execute
            options: report options
            output: output I/O object
        """

        # Default to 50 documents if not specified
        topn = options.get("topn", 50)

        for name, config in queries:
            query = config["query"]
            columns = config["columns"]

            # Write query string
            self.query(output, name, query)

            # Write separator
            self.separator(output)

            # Query for best matches
            results = Query.search(self.embeddings, self.cur, query, topn, options.get("threshold"))

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

        for x, uid in enumerate(documents):
            # Get article metadata
            self.cur.execute(
                "SELECT Published, Title, Reference, Publication, Source, Entry, Id FROM articles WHERE id = ?",
                [uid],
            )
            article = self.cur.fetchone()

            if x and x % 100 == 0:
                print(f"Processed {x} documents", end="\r")

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
        Builds a dict of calculated fields for a given document. This method calculates
        constant field columns and derived query columns. Derived query columns run through
        an embedding search and either run an additional QA query to extract a value or
        use the top n embedding search matches.

        Args:
            uid: article id
            metadata: query metadata

        Returns:
            {name: value} containing derived column values
        """

        # Parse column parameters
        fields, params = self.params(metadata)

        # Different type of calculations
        #  1. Similarity query
        #  2. Extractor query (similarity + question)
        #  3. Question-answering on other field
        queries, extractions, questions = [], [], []

        # Retrieve indexed document text for article
        sections = self.sections(uid)
        texts = [text for _, text in sections]

        for name, query, question, snippet, _, _, matches, _ in params:
            if query.startswith("$"):
                questions.append((name, query.replace("$", ""), question, snippet))
            elif matches:
                queries.append((name, query, matches))
            else:
                extractions.append((name, query, question, snippet))

        # Run all extractor queries against document text
        results = self.rag.query([query for _, query, _ in queries], texts)

        # Only execute embeddings queries for columns with matches set
        for x, (name, query, matches) in enumerate(queries):
            if results[x]:
                # Get topn text matches
                topn = [text for _, text, _ in results[x]][:matches]

                # Join results into String and return
                value = [self.resolve(params, sections, uid, name, value) for value in topn]
                fields[name] = "\n\n".join(value) if value else ""
            else:
                fields[name] = ""

        # Add extraction fields
        if extractions:
            for name, value in self.rag(extractions, texts):
                # Resolves the full value based on column parameters
                fields[name] = self.resolve(params, sections, uid, name, value) if value else ""

        # Add question fields
        for name, value in self.rag(questions, texts):
            # Resolves the full value based on column parameters
            fields[name] = self.resolve(params, sections, uid, name, value) if value else ""

        return fields

    def params(self, metadata):
        """
        Process and prepare parameters using input metadata.

        Args:
            metadata: query metadata

        Returns:
            fields, params - constant field values, query parameters for query columns
        """

        # Derived field values
        fields = {}

        # Query column parameters
        params = []

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

                # Additional context parameters
                section = column.get("section", False)
                surround = column.get("surround", 0)
                matches = column.get("matches", 0)
                dtype = column.get("dtype")
                snippet = column.get("snippet", False)
                snippet = True if section or surround else snippet

                params.append(
                    (
                        column["name"],
                        query,
                        question,
                        snippet,
                        section,
                        surround,
                        matches,
                        dtype,
                    )
                )

        return fields, params

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

    def sections(self, uid):
        """
        Retrieves all sections as list for article with given uid.

        Args:
            uid: article id

        Returns:
            list of section text elements
        """

        # Retrieve indexed document text for article
        self.cur.execute(Index.SECTION_QUERY + " WHERE article = ? ORDER BY id", [uid])

        # Get list of document text sections
        sections = []
        for sid, name, text in self.cur.fetchall():
            if not self.embeddings.isweighted() or not name or not re.search(Index.SECTION_FILTER, name.lower()) or self.options.get("allsections"):
                # Check that section has at least 1 token
                if Tokenizer.tokenize(text):
                    sections.append((sid, text))

        return sections

    def resolve(self, params, sections, uid, name, value):
        """
        Fully resolves a value from an extractor call.

         - If section=True, this method pull the full section text
         - If surround is specified, this method will pull the surrounding text
         - Otherwise, the original value is returned

        Args:
            params: query parameters
            sections: section text
            uid: article id
            name: column name
            value: initial query value after running through extractor process

        Returns:
            resolved value
        """

        # Get all column parameters
        index = [params.index(x) for x in params if x[0] == name][0]
        _, _, _, _, section, surround, _, dtype = params[index]

        if value:
            # Find matching section
            sid = [sid for sid, text in sections if value in text]

            if sid:
                sid = sid[0]

                if section:
                    # Get full text for matching subsection
                    value = self.subsection(uid, sid)
                elif surround:
                    value = self.surround(uid, sid, surround)

            # Column dtype formatting
            if dtype == "int":
                value = Column.integer(value)
            elif isinstance(dtype, list):
                value = Column.categorical(self.labels, value, dtype)
            elif dtype in ["days", "weeks", "months", "years"]:
                value = Column.duration(value, dtype)

        return value

    def subsection(self, uid, sid):
        """
        Extracts all subsection text for columns with section=True.

        Args:
            uid: article id
            sid: section id

        Returns:
            full text for matching section
        """

        self.cur.execute(
            "SELECT Text FROM sections WHERE article = ? AND name = (SELECT name FROM sections WHERE id = ?)",
            [uid, sid],
        )
        return " ".join([x[0] for x in self.cur.fetchall()])

    def surround(self, uid, sid, size):
        """
        Extracts surrounding text for section with specified id.

        Args:
            uid: article id
            sid: section id
            size: number of surrounding lines to extract from each side

        Returns:
            matching text with surrounding context
        """

        self.cur.execute(
            "SELECT Text FROM sections WHERE article = ? AND id in (SELECT id FROM sections WHERE id >= ? AND id <= ?) AND "
            + "name = (SELECT name FROM sections WHERE id = ?)",
            [uid, sid - size, sid + size, sid],
        )

        return " ".join([x[0] for x in self.cur.fetchall()])

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
