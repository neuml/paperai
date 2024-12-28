ARG BASE_IMAGE=python:3.9-slim
FROM $BASE_IMAGE
LABEL maintainer="NeuML"
LABEL repository="paperai"

# Set Python version (i.e. 3, 3.9)
ARG PYTHON_VERSION=3

# Locale environment variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required packages
RUN apt-get update && \
    apt-get -y --no-install-recommends install libgomp1 gcc g++ python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python3-pip wget && \
    rm -rf /var/lib/apt/lists

# Install paperai project and dependencies
RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
    python -m pip install --no-cache-dir -U pip wheel setuptools && \
    python -m pip install --no-cache-dir paperai

# Cleanup build packages
RUN apt-get -y purge gcc g++ python${PYTHON_VERSION}-dev && apt-get -y autoremove

# Create paperetl directories
RUN mkdir -p paperetl/data paperetl/report

# Start script
ENTRYPOINT ["/bin/bash"]
