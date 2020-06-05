#!/usr/bin/env bash

# Check that only one argument is passed
if [[ $# -ne 3 ]]; then
    echo ""
    echo "[ERROR] Illegal number of parameters, one release prefix and two file names for the output are required. Run as:"
    echo "> $0 release_prefix evidence_count.txt disease_count.txt"
    echo ""
    exit 1
fi


release_prefix=$1
evidence_count_file=$2
disease_count_file=$3

# Make dir named as the release and work in there
mkdir -p $release_prefix/evidence_files
cd $release_prefix/evidence_files

# Create output files
touch $evidence_count_file
touch $disease_count_file

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
    # Only process lines with JSON objects to avoid issues with first line in progeny file
    gunzip -c $evidence_file | grep "^{" > ${evidence_file}.json
    jq -r '.sourceID' ${evidence_file}.json | cut -f 1 | sort | uniq -c | tee -a $evidence_count_file
    jq -r '[.sourceID, .disease.id] | @tsv' ${evidence_file}.json | sort -u | cut -f 1 | uniq -c | tee -a $disease_count_file
    rm ${evidence_file}.json
done