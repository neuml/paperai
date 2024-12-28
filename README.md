<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/paperai/master/logo.png"/>
</p>

<p align="center">
    <b>Semantic search and workflows for medical/scientific papers</b>
</p>

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
        <img src="https://img.shields.io/coverallsCoverage/github/neuml/paperai" alt="Coverage Status">
    </a>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

paperai is a semantic search and workflow application for medical/scientific papers.

![demo](https://raw.githubusercontent.com/neuml/paperai/master/demo.png)

Applications range from semantic search indexes that find matches for medical/scientific queries to full-fledged reporting applications powered by machine learning.

![architecture](https://raw.githubusercontent.com/neuml/paperai/master/images/architecture.png#gh-light-mode-only)
![architecture](https://raw.githubusercontent.com/neuml/paperai/master/images/architecture-dark.png#gh-dark-mode-only)

paperai and/or NeuML has been recognized in the following articles:

- [Machine-Learning Experts Delve Into 47,000 Papers on Coronavirus Family](https://www.wsj.com/articles/machine-learning-experts-delve-into-47-000-papers-on-coronavirus-family-11586338201)
- [Data scientists assist medical researchers in the fight against COVID-19](https://cloud.google.com/blog/products/ai-machine-learning/how-kaggle-data-scientists-help-with-coronavirus)
- [CORD-19 Kaggle Challenge Awards](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/discussion/161447)

## Installation

The easiest way to install is via pip and PyPI

```
pip install paperai
```

Python 3.9+ is supported. Using a Python [virtual environment](https://docs.python.org/3/library/venv.html) is recommended.

paperai can also be installed directly from GitHub to access the latest, unreleased features.

```
pip install git+https://github.com/neuml/paperai
```

See [this link](https://neuml.github.io/txtai/install/#environment-specific-prerequisites) to help resolve environment-specific install issues.

### Docker

Run the steps below to build a docker image with paperai and all dependencies.

```
wget https://raw.githubusercontent.com/neuml/paperai/master/docker/Dockerfile
docker build -t paperai .
docker run --name paperai --rm -it paperai
```

paperetl can be added in to have a single image to index and query content. Follow the instructions to build a [paperetl docker image](https://github.com/neuml/paperetl#docker) and then run the following.

```
docker build -t paperai --build-arg BASE_IMAGE=paperetl --build-arg START=/scripts/start.sh .
docker run --name paperai --rm -it paperai
```

## Examples

The following notebooks and applications demonstrate the capabilities provided by paperai.

### Notebooks

| Notebook  | Description  |       |
|:----------|:-------------|------:|
| [Introducing paperai](https://github.com/neuml/paperai/blob/master/examples/01_Introducing_paperai.ipynb) | Overview of the functionality provided by paperai | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/neuml/paperai/blob/master/examples/01_Introducing_paperai.ipynb) |

### Applications

| Application  | Description  |
|:----------|:-------------|
| [Search](https://github.com/neuml/paperai/blob/master/examples/search.py) | Search a paperai index. Set query parameters, execute searches and display results. |

## Building a model

paperai indexes databases previously built with [paperetl](https://github.com/neuml/paperetl). The following shows how to create a new paperai index.

1. (Optional) Create an index.yml file

    paperai uses the default txtai embeddings configuration when not specified. Alternatively, an index.yml file can be specified that takes all the same options as a txtai embeddings instance. See the [txtai documentation](https://neuml.github.io/txtai/embeddings/configuration) for more on the possible options. A simple example is shown below.

    ```
    path: sentence-transformers/all-MiniLM-L6-v2
    content: True
    ```

2. Build embeddings index

    ```
    python -m paperai.index <path to input data> <optional index configuration>
    ```

The paperai.index process requires an input data path and optionally takes index configuration. This configuration can either be a vector model path or an index.yml configuration file.

## Running queries

The fastest way to run queries is to start a paperai shell

```
paperai <path to model directory>
```

A prompt will come up. Queries can be typed directly into the console.

## Building a report file

Reports support generating output in multiple formats. An example report call:

```
python -m paperai.report report.yml 50 md <path to model directory>
```

The following report formats are supported:

- Markdown (Default) - Renders a Markdown report. Columns and answers are extracted from articles with the results stored in a Markdown file.
- CSV - Renders a CSV report. Columns and answers are extracted from articles with the results stored in a CSV file.
- Annotation - Columns and answers are extracted from articles with the results annotated over the original PDF files. Requires passing in a path with the original PDF files.

In the example above, a file named report.md will be created. Example report configuration files can be found [here](https://github.com/neuml/cord19q/tree/master/tasks).

## Tech Overview

paperai is a combination of a [txtai](https://github.com/neuml/txtai) embeddings index and a SQLite database with the articles. Each article is parsed into sentences and stored in SQLite along with the article metadata. Embeddings are built over the full corpus.

Multiple entry points exist to interact with the model.

- paperai.report - Builds a report for a series of queries. For each query, the top scoring articles are shown along with matches from those articles. There is also a highlights section showing the most relevant results.
- paperai.query - Runs a single query from the terminal
- paperai.shell - Allows running multiple queries from the terminal
