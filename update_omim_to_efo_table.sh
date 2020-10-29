#!/usr/bin/env bash

# Download latest EFO owl file
echo "Downloading latest EFO owl file"
echo "curl -L -o efo_latest.owl https://github.com/EBISPOT/efo/releases/latest/download/efo.owl"
curl -L -o efo_latest.owl https://github.com/EBISPOT/efo/releases/latest/download/efo.owl

# Use ROBOT to extract xrefs to OMIM from EFO owl file
echo "Querying owl file"
echo  "robot query --input efo_latest.owl --query ../data_scripts/efo_omim_xrefs.sparql omim_to_efo.tsv"
robot query --input efo_latest.owl --query ../data_scripts/efo_omim_xrefs.sparql omim_to_efo.tsv

# Clean output to match required format
sed 's/["|<|>|?]//g' omim_to_efo.tsv | sed 's/OMIM://' > omim_to_efo.txt

rm omim_to_efo.tsv
echo "DONE. Now update the file in GitHub (https://github.com/opentargets/platform_semantic/blob/master/resources/xref_mappings/omim_to_efo.txt)"