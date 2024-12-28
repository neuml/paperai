"""
Query module
"""

import datetime
import re
import sys

from rich.console import Console

from txtai.pipeline import Tokenizer

from .highlights import Highlights
from .models import Models


class Query:
    """
    Methods to query an embeddings index.
    """

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
        threshold = threshold if threshold is not None else 0.25

        results = []

        # Get list of required and prohibited tokens
        must = [token.strip("+") for token in query.split() if token.startswith("+") and len(token) > 1]
        mnot = [token.strip("-") for token in query.split() if token.startswith("-") and len(token) > 1]

        # Tokenize search query, if necessary
        query = Tokenizer.tokenize(query) if embeddings.isweighted() else query

        # Retrieve topn * 5 to account for duplicate matches
        for result in embeddings.search(query, topn * 5):
            uid, score = (result["id"], result["score"]) if isinstance(result, dict) else result

            if score >= threshold:
                cur.execute("SELECT Article, Text FROM sections WHERE id = ?", [uid])

                # Get matching row
                sid, text = cur.fetchone()

                # Add result if:
                #   - all required tokens are present or there are not required tokens AND
                #   - all prohibited tokens are not present or there are not prohibited tokens
                if (not must or all(token.lower() in text.lower() for token in must)) and (
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
            if score >= 0.1:
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
        topn = sorted(documents, key=lambda k: max(x[0] for x in documents[k]), reverse=True)[:topn]
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

        # Create console printer
        console = Console(soft_wrap=True)
        with console.capture() as output:
            # Print query
            console.print(f"[dark_orange]Query: {query}[/dark_orange]")
            console.print()

            # Execute query
            results = Query.search(embeddings, cur, query, topn, threshold)

            # Extract top sections as highlights
            highlights = Query.highlights(results, int(topn / 5))
            if highlights:
                console.print("[deep_sky_blue1]Highlights[/deep_sky_blue1]")
                for highlight in highlights:
                    console.print(
                        (f"[bright_blue] - {Query.text(highlight)}[/bright_blue]"),
                        highlight=False,
                    )

                console.print()

            # Get results grouped by document
            documents = Query.documents(results, topn)

            # Article header
            console.print("[deep_sky_blue1]Articles[/deep_sky_blue1]")
            console.print()

            # Print each result, sorted by max score descending
            for uid in sorted(documents, key=lambda k: sum(x[0] for x in documents[k]), reverse=True):
                cur.execute(
                    "SELECT Title, Published, Publication, Entry, Id, Reference FROM articles WHERE id = ?",
                    [uid],
                )
                article = cur.fetchone()

                console.print(f"Title: {article[0]}", highlight=False)
                console.print(f"Published: {Query.date(article[1])}", highlight=False)
                console.print(f"Publication: {article[2]}", highlight=False)
                console.print(f"Entry: {article[3]}", highlight=False)
                console.print(f"Id: {article[4]}", highlight=False)
                console.print(f"Reference: {article[5]}")

                # Print top matches
                for score, text in documents[uid]:
                    console.print(
                        f"[bright_blue] - ({score:.4f}): {Query.text(text)}[/bright_blue]",
                        highlight=False,
                    )

                console.print()

        # Print console output
        print(output.get())

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
