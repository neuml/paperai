#!/bin/bash

# Download and unpack vector model
mkdir -p $1
wget -N https://github.com/neuml/paperai/releases/download/v1.3.0/cord19-300d.magnitude.gz -P $1
gunzip $1/cord19-300d.magnitude.gz
