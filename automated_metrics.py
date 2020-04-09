#exec(open('ot_metrics/automated_metrics.py').read())
import json
import pandas as pd
from elasticsearch import Elasticsearch
import argparse

__copyright__ = "Copyright 2014-2019, Open Targets"
__author__ = "Michaela Spitzer, Asier Gonzalez"
__credits__   = ["Michaela Spitzer", "Asier Gonzalez"]
__license__   = "Apache 2.0"
__version__   = "1.2.8"
__maintainer__= "Asier Gonzalez"
__email__     = ["data@opentargets.org"]
__status__    = "Prototype"

def connect_elasticsearch(host, port):
    _es = Elasticsearch([{'host': host, 'port': port}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es

def build_nr_evidence_query():
    """ Build query to get number of valid evidence strings """
    query_nr_evidence_strings = {"query": { "match_all": {} }, "aggs": {"evidence_string_numbers": {"terms": {"field": "private.datasource.keyword","size": 20 }}}, "size": 0}
    return query_nr_evidence_strings

def build_nr_invalid_evidence_query():
    """ Build query to get number of invalid evidence strings """
    query_nr_inv_evidence_strings = {"query": { "match_all": {} }, "aggs": {"evidence_string_numbers": {"terms": {"field": "data_source.keyword","size": 20 }}}, "size": 0}
    return query_nr_inv_evidence_strings

def build_nr_evidence_score0_query():
    """ Build query to get number of evidence strings with score == 0 """
    query_nr_evidence_strings_score0 = {"query": {"match": {"scores.association_score": 0}},"aggs": {"evidence_string_numbers": {"terms": {"field": "private.datasource.keyword","size": 20}}}, "size": 0}
    return query_nr_evidence_strings_score0

def build_nr_assocs_per_datasource_query():
    """ Build query to get number of associations each data sources contribute to """
    query_associations = {"query": {"match_all": {}},"size": 0,
                          "aggs": {
                              "counts": {
                                  "terms": {"field": "private.facets.datasource.keyword","size": 100},
                                  "aggs": {
                                      "uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},
                                      "uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}},
                              "uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},
                              "uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}},
                              "counts_direct": {
                                  "aggs": {
                                      "counts": {"terms": {"field": "private.facets.datasource.keyword","size": 100},
                                                 "aggs": {
                                                     "uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},
                                                     "uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}},
                                      "uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},
                                      "uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}},
                                  "filter": {"term": {"is_direct": "true"}}},
                              "direct_counts_td": {"filter": {"term": {"is_direct": "true"}},
                                                   "aggs": {
                                                       "uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},
                                                       "uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}}}}

    return query_associations

def es_search(es,prefix, index, query):
    """ Query elasticsearch search endpoint """
    return es.search(prefix + index, json.dumps(query), request_timeout=30)

def process_es_response(valid_evidence, invalid_evidence, score0_evidence, counts_associations, outfile):
    # Create a dictionary for all 20 datasources
    datasources = {'genomics_england':{},
                   'ot_genetics_portal': {},
                   'gene2phenotype': {},
                   'phewas_catalog': {},
                   'uniprot': {},
                   'uniprot_literature': {},
                   'uniprot_somatic': {},
                   'eva': {},
                   'eva_somatic': {},
                   'cancer_gene_census':{},
                   'intogen': {},
                   'chembl':{},
                   'reactome': {},
                   'slapenrich': {},
                   'progeny': {},
                   'sysbio': {},
                   'crispr':{},
                   'expression_atlas': {},
                   'phenodigm': {},
                   'europepmc':{}
                   }

    # Create fields for all 8 parameters of interest
    for key in datasources:
        datasources[key]={
            'valid_evidence_strings': 0,
            'invalid_evidence_strings': 0,
            'score_is_0': 0,
            'associations_direct': 0,
            'diseases_direct': 0,
            'targets_direct': 0,
            'associations_all': 0,
            'diseases_all': 0
        }
    # Retrieve the numbers from each of the 4 ES queries
    for item in valid_evidence['aggregations']['evidence_string_numbers']['buckets']:
        datasources[item['key']]['valid_evidence_strings'] = item['doc_count']
    for item in invalid_evidence['aggregations']['evidence_string_numbers']['buckets']:
        datasources[item['key']]['invalid_evidence_strings'] = item['doc_count']
    for item in score0_evidence['aggregations']['evidence_string_numbers']['buckets']:
        datasources[item['key']]['score_is_0'] = item['doc_count']

    for item in counts_associations['aggregations']['counts_direct']['counts']['buckets']:
        datasources[item['key']]['associations_direct'] = item['doc_count']
        datasources[item['key']]['diseases_direct'] = item['uniq_diseases']['value']
        datasources[item['key']]['targets_direct'] = item['uniq_targets']['value']

    for item in counts_associations['aggregations']['counts']['buckets']:
        datasources[item['key']]['associations_all'] = item['doc_count']
        datasources[item['key']]['diseases_all'] = item['uniq_diseases']['value']

    # Collect the data in a panda dataframe to write into a csv file
    df = pd.DataFrame(columns=datasources['eva'].keys())
    myrow=0
    for key in datasources:
        df.loc[myrow] = list(datasources[key].values())
        myrow=myrow+1

    df.insert(0, "datasource", datasources.keys(), True)
    df.to_csv(outfile, index=False)

def main():

    # Parse CLI parameters
    parser = argparse.ArgumentParser(description='Script that extracts metrics from elasticsearch server.')
    parser.add_argument('--esPrefix', help='Prefix of ES indices, e.g. 20.04', type=str, required=True)
    parser.add_argument('-o','--outputFile', help='Name of the output file', type=str, default='ot_metrics.csv')
    parser.add_argument('--host', help='Name or IP address of the ES server, "localhost" by default', type=str, default='localhost')
    parser.add_argument('--port', help='Port number where ES is listening, 9200 by default', type=int, default=9200)
    args = parser.parse_args()

    # Parse input parameters
    es_prefix = args.esPrefix
    outfile = args.outputFile
    host = args.host
    port = args.port

    # Connect to ES
    es = connect_elasticsearch(host, port)

    if es is not None:
        query_nr_evidence_strings = build_nr_evidence_query()
        valid_evidence = es_search(es, es_prefix, "_evidence-data", query_nr_evidence_strings)

        query_nr_inv_evidence_strings = build_nr_invalid_evidence_query()
        invalid_evidence = es_search(es, es_prefix, "_invalid-evidence-data", query_nr_inv_evidence_strings)

        query_nr_evidence_strings_score0 = build_nr_evidence_score0_query()
        score0_evidence = es_search(es, es_prefix, "_evidence-data", query_nr_evidence_strings_score0)

        query_associations_per_datasource = build_nr_assocs_per_datasource_query()
        counts_associations = es_search(es, es_prefix, "_association-data", query_associations_per_datasource)

        process_es_response(valid_evidence, invalid_evidence, score0_evidence, counts_associations, outfile)



if __name__ == "__main__":
    main()