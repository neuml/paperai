"""
Enhanced API that also returns document metadata
"""

import os
import sqlite3

import txtai.api

from paperai.query import Query

class API(txtai.api.API):
    """
    Extended API on top of txtai to return enriched query results.
    """

    def search(self, query, request):
        """
        Extends txtai API to enrich results with content.

        Args:
            query: query text
            request: FastAPI request

        Returns:
            query results
        """

        if self.embeddings:
            dbfile = os.path.join(self.config["path"], "articles.sqlite")
            limit = self.limit(request.query_params.get("limit"))
            threshold = float(request.query_params["threshold"]) if "threshold" in request.query_params else None

            with sqlite3.connect(dbfile) as db:
                cur = db.cursor()

                # Query for best matches
                results = Query.search(self.embeddings, cur, query, limit, threshold)

                # Get results grouped by document
                documents = Query.documents(results, limit)

                articles = []

                # Print each result, sorted by max score descending
                for uid in sorted(documents, key=lambda k: sum([x[0] for x in documents[k]]), reverse=True):
                    cur.execute("SELECT Title, Published, Publication, Design, Size, Sample, Method, Entry, Id, Reference " +
                                "FROM articles WHERE id = ?", [uid])
                    article = cur.fetchone()

                    score = max([score for score, text in documents[uid]])
                    matches = [text for _, text in documents[uid]]

                    article = {"id": article[8], "score": score, "title": article[0], "published": Query.date(article[1]), "publication": article[2],
                               "design": Query.design(article[3]), "sample": Query.sample(article[4], article[5]), "method": Query.text(article[6]),
                               "entry": article[7], "reference": article[9], "matches": matches}

                    articles.append(article)

                return articles

        return None
