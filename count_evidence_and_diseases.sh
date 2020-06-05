#!/usr/bin/env bash

# Check that only one argument is passed
if [[ $# -ne 1 ]]; then
    echo ""
    echo "[ERROR] Illegal number of parameters, one release prefix is required. Run as:"
    echo "> $0 release_prefix"
    echo ""
    exit 1
fi


release_prefix=$1

# Make dir named as the release and work in there
mkdir -p $release_prefix/evidence_files
cd $release_prefix/evidence_files

# Download evidence files
for datasource in $(gsutil ls gs://open-targets-data-releases/${release_prefix}/input/evidence-files/*gz)
do
    echo "Downloading $datasource"
    gsutil cp $datasource .
done

# Delete GWAS file as it isn't used anymore
rm -f gwas*

# Iterate through all the files uncompress them, count the rows and the diseases
for evidence_file in *.json.gz
do
    gunzip -c $evidence_file > ${evidence_file}.json
    jq '.sourceID' ${evidence_file}.json | cut -f 1 | sort | uniq -c
    jq -r '[.sourceID, .disease.id] | @tsv' ${evidence_file}.json | sort -u | cut -f 1 | uniq -c
    rm ${evidence_file}.json
done