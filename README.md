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

Python 3.7+ is supported. Using a Python [virtual environment](https://docs.python.org/3/library/venv.html) is recommended.

paperai can also be installed directly from GitHub to access the latest, unreleased features.

    pip install git+https://github.com/neuml/paperai

See [this link](https://neuml.github.io/txtai/install/#environment-specific-prerequisites) to help resolve environment-specific install issues.

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

The following notebooks and applications demonstrate the capabilities provided by paperai.

### Notebooks

| Notebook     |      Description      |
|:----------|:-------------|
| [CORD-19 Analysis with Sentence Embeddings](https://www.kaggle.com/davidmezzetti/cord-19-analysis-with-sentence-embeddings) | Builds paperai-based submissions for the CORD-19 Challenge |
| [CORD-19 Report Builder](https://www.kaggle.com/davidmezzetti/cord-19-report-builder) | Template for building new reports |

### Applications

| Application  | Description  |
|:----------|:-------------|
| [Search](https://github.com/neuml/paperai/blob/master/examples/search.py) | Search a paperai index. Set query parameters, execute searches and display results. |

## Building a model

paperai indexes databases previously built with [paperetl](https://github.com/neuml/paperetl). paperai currently supports querying SQLite databases.

The following sections show how to build an embeddings index for a SQLite articles database. This example assumes the database and model path is cord19/models. Substitute as appropriate.

1. Get vector model

    Run following script to download [CORD-19 fastText vectors](https://github.com/neuml/paperai/releases/download/v1.3.0/cord19-300d.magnitude.gz)

    ```bash
    scripts/getvectors.sh cord19/vectors
    ```

    A full vector model build for fastText models can optionally be run with the following command.

    ```bash
    python -m paperai.vectors cord19/models
    ```

2. Build embeddings index

    ```bash
    python -m paperai.index cord19/models cord19/vectors/cord19-300d.magnitude
    ```

The paperai.index process takes two required arguments, the model path and the vector model path. In this case, the vector model is a CORD-19 fastText model but it can also be any supported [transformers model](https://huggingface.co/models?pipeline_tag=sentence-similarity).

## Building a report file

Reports support generating output in multiple formats. An example report call:

    python -m paperai.report report.yml 50 md cord19/models

The following report formats are supported:

- Markdown (Default) - Renders a Markdown report. Columns and answers are extracted from articles with the results stored in a Markdown file.
- CSV - Renders a CSV report. Columns and answers are extracted from articles with the results stored in a CSV file.
- Annotation - Columns and answers are extracted from articles with the results annotated over the original PDF files. Requires passing in a path with the original PDF files.

In the example above, a file named report.md will be created. Example report configuration files can be found [here](https://github.com/neuml/cord19q/tree/master/tasks).

## Running queries

The fastest way to run queries is to start a paperai shell

    paperai cord19/models

A prompt will come up. Queries can be typed directly into the console.

## Tech Overview

The model is a combination of a sentence embeddings index and a SQLite database with the articles. Each article is parsed into sentences and stored in SQLite along with the article metadata. Sentence embeddings are built over the full corpus. The sentence embeddings index only uses tagged articles, which helps produce the most relevant results.

Multiple entry points exist to interact with the model.

- paperai.report - Builds a markdown report for a series of queries. For each query, the best articles are shown, top matches from those articles and a highlights section which shows the most relevant sections from the embeddings search for the query.
- paperai.query - Runs a single query from the terminal
- paperai.shell - Allows running multiple queries from the terminal
