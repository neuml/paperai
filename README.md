<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/paperai/master/logo.png"/>
</p>

<h3 align="center">
    <p>AI-powered literature discovery and review engine for medical/scientific papers</p>
</h3>

<p align="center">
    <a href="https://github.com/neuml/paperai/releases">
        <img src="https://img.shields.io/github/release/neuml/paperai.svg?style=flat&color=success" alt="Version"/>
    </a>
    <a href="https://github.com/neuml/paperai/releases">
        <img src="https://img.shields.io/github/release-date/neuml/paperai.svg?style=flat&color=blue" alt="GitHub Release Date"/>
    </a>
    <a href="https://github.com/neuml/paperai/issues">
        <img src="https://img.shields.io/github/issues/neuml/paperai.svg?style=flat&color=success" alt="GitHub issues"/>
    </a>
    <a href="https://github.com/neuml/paperai">
        <img src="https://img.shields.io/github/last-commit/neuml/paperai.svg?style=flat&color=blue" alt="GitHub last commit"/>
    </a>
    <a href="https://github.com/neuml/paperai/actions?query=workflow%3Abuild">
        <img src="https://github.com/neuml/paperai/workflows/build/badge.svg" alt="Build Status"/>
    </a>
    <a href="https://coveralls.io/github/neuml/paperai?branch=master">
        <img src="https://img.shields.io/coveralls/github/neuml/paperai" alt="Coverage Status">
    </a>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

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

### Docker

A Dockerfile with commands to install paperai, all dependencies and scripts is available in this repository.

Clone this git repository and run the following to build and run the Docker image.

```bash
docker build -t paperai -f docker/Dockerfile .
docker run --name paperai --rm -it paperai
```

This will bring up a paperai command shell. Standard Docker commands can be used to copy files over or commands can be run directly in the shell to retrieve input content. All scripts in the following examples are available in this environment.

[paperetl's Dockerfile](https://github.com/neuml/paperetl#docker) can be combined with this Dockerfile to have a single image that can index and query content. The files from the paperetl project scripts directory needs to be placed in paperai's scripts directory. The paperetl Dockerfile also needs to be copied over (it's referenced as paperetl.Dockerfile here).

```bash
docker build -t base -f docker/Dockerfile .
docker build -t paperai --build-arg BASE_IMAGE=base -f docker/paperetl.Dockerfile .
docker run --name paperai --rm -it paperai
```

## Examples

The following notebooks demonstrate the capabilities provided by paperai.

### Notebooks

| Notebook     |      Description      |
|:----------|:-------------|
| [CORD-19 Analysis with Sentence Embeddings](https://www.kaggle.com/davidmezzetti/cord-19-analysis-with-sentence-embeddings) | Builds paperai-based submissions for the CORD-19 Challenge |
| [CORD-19 Report Builder](https://www.kaggle.com/davidmezzetti/cord-19-report-builder) | Template for building new reports |

## Building a model
paperai indexes databases previously built with [paperetl](https://github.com/neuml/paperetl). paperai currently supports querying SQLite databases.

The following sections show how to build an index for a SQLite articles database.

This example assumes the database and model path is cord19/models. Substitute as appropriate.

1. Download [CORD-19 fastText vectors](https://github.com/neuml/paperai/releases/download/v1.3.0/cord19-300d.magnitude.gz)

    ```bash
    scripts/getvectors.sh cord19/vectors
    ```

    A full vector model build can optionally be run with the following command.

    ```bash
    python -m paperai.vectors cord19/models
    ```

    [CORD-19 fastText vectors](https://www.kaggle.com/davidmezzetti/cord19-fasttext-vectors) are also available on Kaggle.

2. Build embeddings index

    ```bash
    python -m paperai.index cord19/models cord19/vectors/cord19-300d.magnitude
    ```

The paperai.index process takes two optional arguments, the model path and the vector file path. The default model location is ~/.cord19 if
no parameters are passed in.

## Building a report file
Reports support generating output in multiple formats. An example report call:

    python -m paperai.report tasks/risk-factors.yml 50 md cord19/models

The following report formats are supported:

- Markdown (Default) - Renders a Markdown report. Columns and answers are extracted from articles with the results stored in a Markdown file.
- CSV - Renders a CSV report. Columns and answers are extracted from articles with the results stored in a CSV file.
- Annotation - Columns and answers are extracted from articles with the results annotated over the original PDF files. Requires passing in a path with the original PDF files.

In the example above, a file named tasks/risk-factors.md will be created.

## Running queries
The fastest way to run queries is to start a paperai shell

    paperai cord19/models

A prompt will come up. Queries can be typed directly into the console.

## Tech Overview
The tech stack is built on Python and creates a sentence embeddings index with FastText + BM25. Background on this method can be found in this [Medium article](https://towardsdatascience.com/building-a-sentence-embedding-index-with-fasttext-and-bm25-f07e7148d240). 

The model is a combination of a sentence embeddings index and a SQLite database with the articles. Each article is parsed into sentences and stored in SQLite along with the article metadata. FastText vectors are built over the full corpus. The sentence embeddings index only uses tagged articles, which helps produce the most relevant results.

Multiple entry points exist to interact with the model.

- paperai.report - Builds a markdown report for a series of queries. For each query, the best articles are shown, top matches from those articles and a highlights section which shows the most relevant sections from the embeddings search for the query.
- paperai.query - Runs a single query from the terminal
- paperai.shell - Allows running multiple queries from the terminal
