# paperai: AI-powered literature discovery and review engine for medical/scientific papers

[![Version](https://img.shields.io/github/release/neuml/paperai.svg?style=flat&color=success)](https://github.com/neuml/paperai/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/neuml/paperai.svg?style=flat&color=blue)](https://github.com/neuml/paperai/releases)
[![GitHub issues](https://img.shields.io/github/issues/neuml/paperai.svg?style=flat&color=success)](https://github.com/neuml/paperai/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/neuml/paperai.svg?style=flat&color=blue)](https://github.com/neuml/paperai)
[![Build Status](https://github.com/neuml/paperai/workflows/build/badge.svg)](https://github.com/neuml/paperai/actions?query=workflow%3Abuild)
[![Coverage Status](https://img.shields.io/coveralls/github/neuml/paperai)](https://coveralls.io/github/neuml/paperai?branch=master)

![demo](https://raw.githubusercontent.com/neuml/paperai/master/demo.png)

paperai is an AI-powered literature discovery and review engine for medical/scientific papers. paperai helps automate tedious literature reviews allowing researchers to focus on their core work. Queries are run to filter papers with specified criteria. Reports powered by extractive question-answering are run to identify answers to key questions within sets of medical/scientific papers.

paperai was used to analyze the COVID-19 Open Research Dataset (CORD-19), winning multiple awards in the CORD-19 Kaggle challenge.

paperai and/or NeuML has been recognized in the following articles:

- [CORD-19 Kaggle Challenge Awards](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/discussion/161447)
- [Machine-Learning Experts Delve Into 47,000 Papers on Coronavirus Family](https://www.wsj.com/articles/machine-learning-experts-delve-into-47-000-papers-on-coronavirus-family-11586338201)
- [Data scientists assist medical researchers in the fight against COVID-19](https://cloud.google.com/blog/products/ai-machine-learning/how-kaggle-data-scientists-help-with-coronavirus)

## Installation
The easiest way to install is via pip and PyPI

    pip install paperai

You can also install paperai directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/paperai

Python 3.6+ is supported

See [this link](https://github.com/neuml/txtai#installation) to help resolve environment-specific install issues.

## Examples

The following notebooks demonstrate the capabilities provided by paperai.

### Notebooks

| Notebook     |      Description      |
|:----------|:-------------|
| [CORD-19 Analysis with Sentence Embeddings](https://www.kaggle.com/davidmezzetti/cord-19-analysis-with-sentence-embeddings) | Builds paperai-based submissions for the CORD-19 Challenge |
| [CORD-19 Report Builder](https://www.kaggle.com/davidmezzetti/cord-19-report-builder) | Template for building new reports |

## Building a model
paperai indexes databases previously built with [paperetl](https://github.com/neuml/paperetl). paperai currently supports querying SQLite databases.

To build an index for a SQLite articles database:

    # Can optionally use pre-trained vectors
    # https://www.kaggle.com/davidmezzetti/cord19-fasttext-vectors#cord19-300d.magnitude
    # Default location: ~/.cord19/vectors/cord19-300d.magnitude
    python -m paperai.vectors

    # Build embeddings index
    python -m paperai.index

The model will be stored in ~/.cord19

## Building a report file
Reports support generating output in multiple formats. An example report call:

    python -m paperai.report tasks/risk-factors.yml

The following report formats are supported:

- Markdown (Default) - Renders a Markdown report. Columns and answers are extracted from articles with the results stored in a Markdown file.
- CSV - Renders a CSV report. Columns and answers are extracted from articles with the results stored in a CSV file.
- Annotation - Columns and answers are extracted from articles with the results annotated over the original PDF files. Requires passing in a path with the original PDF files.

In the example above, a file named tasks/risk-factors.md will be created.

## Running queries
The fastest way to run queries is to start a paperai shell

    paperai

A prompt will come up. Queries can be typed directly into the console.

## Tech Overview
The tech stack is built on Python and creates a sentence embeddings index with FastText + BM25. Background on this method can be found in this [Medium article](https://towardsdatascience.com/building-a-sentence-embedding-index-with-fasttext-and-bm25-f07e7148d240). 

The model is a combination of a sentence embeddings index and a SQLite database with the articles. Each article is parsed into sentences and stored in SQLite along with the article metadata. FastText vectors are built over the full corpus. The sentence embeddings index only uses tagged articles, which helps produce the most relevant results.

Multiple entry points exist to interact with the model.

- paperai.report - Builds a markdown report for a series of queries. For each query, the best articles are shown, top matches from those articles and a highlights section which shows the most relevant sections from the embeddings search for the query.
- paperai.query - Runs a single query from the terminal
- paperai.shell - Allows running multiple queries from the terminal
