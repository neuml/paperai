"""
Query module
"""

import datetime
import re
import sys

import html2markdown
import mdv

from txtai.pipeline import Tokenizer

from .highlights import Highlights
from .models import Models


class Query:
    """
    Methods to query an embeddings index.
    """

    @staticmethod
    def markdown(text):
        """
        Converts html text to markdown.

        Args:
            text: html text

        Returns:
            text as markdown
        """

        # Remove rel attributes as they are not supported by html2markdown
        text = re.sub(r' rel=".+?">', ">", text)

        # Convert html to markdown
        text = html2markdown.convert(text)

        # Decode [<>&] characters
        return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    @staticmethod
    def escape(text):
        """
        Escapes text to work around issues with mdv double escaping characters.

        Args:
            text: input text

        Returns:
            escaped text
        """

        text = text.replace("<", "¿")
        text = text.replace(">", "Ñ")
        text = text.replace("&", "ž")

        return text

    @staticmethod
    def unescape(text):
        """
        Un-escapes text to work around issues with mdv double escaping characters.

        Args:
            text: input text

        Returns:
            unescaped text
        """

        text = text.replace("¿", "<")
        text = text.replace("Ñ", ">")
        text = text.replace("ž", "&")

        return text

    @staticmethod
    def render(text, theme="592.2129", html=True, tab_length=0):
        """
        Renders input text to formatted text ready to send to the terminal.

        Args:
            text: input html text

        Returns:
            text formatted for print to terminal
        """

        if html:
            # Convert html to markdown
            text = Query.markdown(text)
            text = Query.escape(text)

        text = mdv.main(
            text, theme=theme, c_theme="953.3567", cols=180, tab_length=tab_length
        )

        if html:
            text = Query.unescape(text)

        return text.strip()

    @staticmethod
    def search(embeddings, cur, query, topn, threshold):
        """
        Executes an embeddings search for the input query. Each returned result is resolved
        to the full section row.

        Args:
            embeddings: embeddings model
            cur: database cursor
            query: query text
            topn: number of documents to return
            threshold: require at least this score to include result

        Returns:
            search results
        """

        if query == "*":
            return []

        # Default threshold if None
        threshold = threshold if threshold is not None else 0.6

        results = []

        # Get list of required and prohibited tokens
        must = [
            token.strip("+")
            for token in query.split()
            if token.startswith("+") and len(token) > 1
        ]
        mnot = [
            token.strip("-")
            for token in query.split()
            if token.startswith("-") and len(token) > 1
        ]

        # Tokenize search query
        query = Tokenizer.tokenize(query)

        # Retrieve topn * 5 to account for duplicate matches
        for uid, score in embeddings.search(query, topn * 5):
            if score >= threshold:
                cur.execute("SELECT Article, Text FROM sections WHERE id = ?", [uid])

                # Get matching row
                sid, text = cur.fetchone()

                # Add result if:
                #   - all required tokens are present or there are not required tokens AND
                #   - all prohibited tokens are not present or there are not prohibited tokens
                if (
                    not must or all(token.lower() in text.lower() for token in must)
                ) and (
                    not mnot or all(token.lower() not in text.lower() for token in mnot)
                ):
                    # Save result
                    results.append((uid, score, sid, text))

        return results

    @staticmethod
    def highlights(results, topn):
        """
        Builds a list of highlights for the search results. Returns top ranked sections by importance
        over the result list.

        Args:
            results: search results
            topn: number of highlights to extract

        Returns:
            top ranked sections
        """

        sections = {}
        for uid, score, _, text in results:
            # Filter out lower scored results
            if score >= 0.35:
                sections[text] = (uid, text)

        # Return up to 5 highlights
        return Highlights.build(sections.values(), min(topn, 5))

    @staticmethod
    def documents(results, topn):
        """
        Processes search results and groups by article.

        Args:
            results: search results
            topn: number of documents to return

        Returns:
            results grouped by article
        """

        documents = {}

        # Group by article
        for _, score, article, text in results:
            if article not in documents:
                documents[article] = set()

            documents[article].add((score, text))

        # Sort based on section id, which preserves original order
        for uid in documents:
            documents[uid] = sorted(list(documents[uid]), reverse=True)

        # Get documents with top n best sections
        topn = sorted(
            documents, key=lambda k: max([x[0] for x in documents[k]]), reverse=True
        )[:topn]
        return {uid: documents[uid] for uid in topn}

    @staticmethod
    def all(cur):
        """
        Gets a list of all article ids.

        Args:
            cur: database cursor

        Returns:
            list of all ids as a dict
        """

        cur.execute("SELECT Id FROM articles")
        return {row[0]: None for row in cur.fetchall()}

    @staticmethod
    def authors(authors):
        """
        Formats a short authors string

        Args:
            authors: full authors string

        Returns:
            short author string
        """

        if authors:
            authors = authors.split("; ")[0]
            if "," in authors:
                authors = authors.split(",")[0]
            else:
                authors = authors.split()[-1]

            return f"{authors} et al"

        return None

    @staticmethod
    def date(date):
        """
        Formats a date string.

        Args:
            date: input date string

        Returns:
            formatted date
        """

        if date:
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            # 1/1 dates had no month/day specified, use only year
            if date.month == 1 and date.day == 1:
                return date.strftime("%Y")

            return date.strftime("%Y-%m-%d")

        return None

    @staticmethod
    def text(text):
        """
        Formats match text.

        Args:
            text: input text

        Returns:
            formatted text
        """

        if text:
            # Remove reference links ([1], [2], etc)
            text = re.sub(r"\s*[\[(][0-9, ]+[\])]\s*", " ", text)

            # Remove •
            text = text.replace("•", "")

            # Remove http links
            text = re.sub(r"http.+?\s", " ", text)

        return text

    @staticmethod
    def query(embeddings, db, query, topn, threshold):
        """
        Executes a query against the embeddings model.

        Args:
            embeddings: embeddings model
            db: open SQLite database
            query: query string
            topn: number of query results
            threshold: query match score threshold
        """

        # Default to 10 results if not specified
        topn = topn if topn else 10

        cur = db.cursor()

        print(Query.render(f"#Query: {query}", theme="729.8953") + "\n")

        # Query for best matches
        results = Query.search(embeddings, cur, query, topn, threshold)

        # Extract top sections as highlights
        print(Query.render("# Highlights"))
        for highlight in Query.highlights(results, int(topn / 5)):
            print(Query.render(f"## - {Query.text(highlight)}"))

        print()

        # Get results grouped by document
        documents = Query.documents(results, topn)

        print(Query.render("# Articles") + "\n")

        # Print each result, sorted by max score descending
        for uid in sorted(
            documents, key=lambda k: sum([x[0] for x in documents[k]]), reverse=True
        ):
            cur.execute(
                "SELECT Title, Published, Publication, Entry, Id, Reference FROM articles WHERE id = ?",
                [uid],
            )
            article = cur.fetchone()

            print(f"Title: {article[0]}")
            print(f"Published: {Query.date(article[1])}")
            print(f"Publication: {article[2]}")
            print(f"Entry: {article[3]}")
            print(f"Id: {article[4]}")
            print(f"Reference: {article[5]}")

            # Print top matches
            for score, text in documents[uid]:
                print(
                    Query.render(f"## - ({score:.4f}): {Query.text(text)}", html=False)
                )

            print()

    @staticmethod
    def run(query, topn=None, path=None, threshold=None):
        """
        Executes a query against an index.

        Args:
            query: input query
            topn: number of results
            path: model path
            threshold: query match score threshold
        """

        # Load model
        embeddings, db = Models.load(path)

        # Query the database
        Query.query(embeddings, db, query, topn, threshold)

        # Free resources
        Models.close(db)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        Query.run(
            sys.argv[1],
            int(sys.argv[2]) if len(sys.argv) > 2 else None,
            sys.argv[3] if len(sys.argv) > 3 else None,
            float(sys.argv[4]) if len(sys.argv) > 4 else None,
        )
