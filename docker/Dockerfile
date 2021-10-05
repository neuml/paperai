ARG BASE_IMAGE=ubuntu:18.04
FROM $BASE_IMAGE
LABEL maintainer="NeuML"
LABEL repository="paperai"

# Locale environment variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required packages
RUN apt-get update && \
    apt-get -y --no-install-recommends install libgomp1 gcc g++ python3.7 python3.7-dev python3-pip wget && \
    rm -rf /var/lib/apt/lists

# Install paperai project and dependencies
RUN ln -sf /usr/bin/python3.7 /usr/bin/python && \
    python -m pip install --no-cache-dir -U pip wheel setuptools && \
    python -m pip install --no-cache-dir paperai

# Cleanup build packages
RUN apt-get -y purge gcc g++ python3-dev && apt-get -y autoremove

# Copy paperai scripts
RUN mkdir -p scripts
COPY scripts/ ./scripts/

# Create paperetl directories
RUN mkdir -p cord19/data cord19/report && \
    mkdir -p paperetl/data paperetl/report

# Install vector model
RUN scripts/getvectors.sh cord19/models && \
    scripts/getvectors.sh paperetl/models

# Start script
ENTRYPOINT /bin/bash
