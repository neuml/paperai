"""
Search a paperai index.

Requires streamlit to be installed.
  pip install streamlit
"""

import os
import sqlite3
import sys

import pandas as pd
import streamlit as st

from paperai.models import Models
from paperai.query import Query

class Application:
    """
    Streamlit application.
    """

    def __init__(self, path):
        """
        Creates a new Streamlit application.
        """

        # Default list of columns
        self.columns = [("Title", True), ("Published", False), ("Publication", False), ("Design", False), ("Sample", False),
                        ("Method", False), ("Entry", False), ("Id", False), ("Content", True)]

        # Load model
        self.path = path
        self.embeddings, db = Models.load(path)
        db.close()

    def search(self, query, topn, threshold):
        """
        Executes a search

        Args:
            data: input data
        """

        dbfile = os.path.join(self.path, "articles.sqlite")
        with sqlite3.connect(dbfile) as db:
            cur = db.cursor()

            # Query for best matches
            results = Query.search(self.embeddings, cur, query, topn, threshold)

            # Get results grouped by document
            documents = Query.documents(results, topn)

            articles = []

            # Print each result, sorted by max score descending
            for uid in sorted(documents, key=lambda k: sum([x[0] for x in documents[k]]), reverse=True):
                cur.execute("SELECT Title, Published, Publication, Design, Size, Sample, Method, Entry, Id, Reference " + 
                            "FROM articles WHERE id = ?", [uid])
                article = cur.fetchone()

                matches = "\n".join([text for _, text in documents[uid]])
                matches = matches.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

                title = "<a target='_blank' href='%s'>%s</a>" % (article[9], article[0])

                article = {"Title": title, "Published": Query.date(article[1]), "Publication": article[2], "Design": Query.design(article[3]),
                           "Sample": Query.sample(article[4], article[5]), "Method": Query.text(article[6]), "Entry": article[7],
                           "Id": article[8], "Content": matches}

                articles.append(article)

            return pd.DataFrame(articles)

    def run(self):
        """
        Runs Streamlit application.
        """

        st.sidebar.image("https://github.com/neuml/paperai/raw/master/logo.png", width=256)
        st.sidebar.markdown("## Search parameters")

        # Search parameters
        query = st.text_area("Query")
        topn = st.sidebar.number_input("topn", value=10)
        threshold = st.sidebar.slider("threshold", 0.0, 1.0, 0.6)

        st.markdown("<style>.small-font { font-size: 0.8rem !important;}</style>", unsafe_allow_html=True)
        st.sidebar.markdown("<p class='small-font'>Select columns</p>", unsafe_allow_html=True)
        columns = [column for column, enabled in self.columns if st.sidebar.checkbox(column, enabled)]
        if self.embeddings and query:
            df = self.search(query, topn, threshold)
            st.markdown("<p class='small-font'>%d results</p>" % len(df), unsafe_allow_html=True)

            if not df.empty:
                st.write(df[columns].to_html(escape=False, index=False), unsafe_allow_html=True)

@st.cache(allow_output_mutation=True)
def create(path):
    """
    Creates and caches a Streamlit application.

    Returns:
        Application
    """

    return Application(path)


if __name__ == "__main__":
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    if len(sys.argv) <= 1 or not os.path.isdir(sys.argv[1]):
        st.error("Path to embeddings index not present or invalid")
    else: 
        st.set_page_config(layout="wide")

        # Create and run application
        app = create(sys.argv[1])
        app.run()
