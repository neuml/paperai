# paperai: AI-Powered Literature Discovery and Review Engine for medical/scientific articles

paperai builds an AI-Powered index over sets of medical and scientific articles.

## Installation
You can install paperai directly from GitHub using pip. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/paperai

Python 3.6+ is supported

## Building a model
paperai indexes models previously built with [paperetl](https://github.com/neuml/paperetl). paperai currently supports querying SQLite databases.

To build an index for a SQLite articles database:

    # Can optionally use pre-trained vectors
    # https://www.kaggle.com/davidmezzetti/cord19-fasttext-vectors#cord19-300d.magnitude
    # Default location: ~/.cord19/vectors/cord19-300d.magnitude
    python -m paperai.vectors

    # Build embeddings index
    python -m paperai.index

The model will be stored in ~/.cord19

### Building a report file
A report file is simply a markdown file created from a list of queries. An example report call:

    python -m paperai.report tasks/risk-factors.yml

Once complete a file named tasks/risk-factors.md will be created.

### Running queries
The fastest way to run queries is to start a paperai shell

    paperai

A prompt will come up. Queries can be typed directly into the console.

### Tech Overview
The tech stack is built on Python and creates a sentence embeddings index with FastText + BM25. Background on this method can be found in this [Medium article](https://towardsdatascience.com/building-a-sentence-embedding-index-with-fasttext-and-bm25-f07e7148d240) and an existing repository using this method [codequestion](https://github.com/neuml/codequestion).

The model is a combination of the sentence embeddings index and a SQLite database with the articles. Each article is parsed into sentences and stored in SQLite along with the article metadata. FastText vectors are built over the full corpus. The sentence embeddings index only uses tagged articles, which helps produce most relevant results.

Multiple entry points exist to interact with the model.

- paperai.report - Builds a markdown report for a series of queries. For each query, the best articles are shown, top matches from those articles and a highlights section which shows the most relevant sections from the embeddings search for the query.
- paperai.query - Runs a single query from the terminal
- paperai.shell - Allows running multiple queries from the terminal
