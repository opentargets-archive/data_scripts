#exec(open('ot_metrics/automated_metrics.py').read())
import json
import pandas as pd
from elasticsearch import Elasticsearch

__copyright__ = "Copyright 2014-2019, Open Targets"
__author__ = "Michaela Spitzer, Asier Gonzalez"
__credits__   = ["Michaela Spitzer", "Asier Gonzalez"]
__license__   = "Apache 2.0"
__version__   = "1.2.8"
__maintainer__= "Asier Gonzalez"
__email__     = ["data@opentargets.org"]
__status__    = "Prototype"

def connect_elasticsearch():
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es

# Connect to ES and run the queries
es = connect_elasticsearch()
if es is not None:
    # Get nr of valid evidence strings
    query_nr_evidence_strings = {"query": { "match_all": {} }, "aggs": {"evidence_string_numbers": {"terms": {"field": "private.datasource.keyword","size": 20 }}}, "size": 0}
    valid_evidence = es.search('19.09_evidence-data', json.dumps(query_nr_evidence_strings))
    # Get number of invalid evidence strings
    query_nr_inv_evidence_strings = {"query": { "match_all": {} }, "aggs": {"evidence_string_numbers": {"terms": {"field": "data_source.keyword","size": 20 }}}, "size": 0}
    invalid_evidence = es.search('19.09_invalid-evidence-data', json.dumps(query_nr_inv_evidence_strings))
    # Get nr of evidence strings with score == 0
    query_nr_evidence_strings_score0 = {"query": {"match": {"scores.association_score": 0}},"aggs": {"evidence_string_numbers": {"terms": {"field": "private.datasource.keyword","size": 20}}}, "size": 0}
    score0_evidence = es.search('19.09_evidence-data', json.dumps(query_nr_evidence_strings_score0))
    # Get nr of associations data sources contribute to
    query_associations = {"query": {"match_all": {}},"size": 0,"aggs": {"counts": {"terms": {"field": "private.facets.datasource.keyword","size": 100},"aggs": {"uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},"uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}},"uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},"uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}},"counts_direct": {"aggs": {"counts": {"terms": {"field": "private.facets.datasource.keyword","size": 100},"aggs": {"uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},"uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}},"uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},"uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}},"filter": {"term": {"is_direct": "true"}}},"direct_counts_td": {"filter": {"term": {"is_direct": "true"}},"aggs": {"uniq_targets": {"cardinality": {"field": "target.gene_info.geneid.keyword"}},"uniq_diseases": {"cardinality": {"field": "disease.efo_info.efo_id.keyword"}}}}}}
    counts_associations = es.search('19.09_association-data', json.dumps(query_associations), request_timeout=30)

# Create a dictionary for all 20 datasources
datasources = {'cancer_gene_census':{},
               'chembl':{},
               'crispr':{},
               'europepmc':{},
               'eva':{},
               'eva_somatic':{},
               'expression_atlas':{},
               'gene2phenotype':{},
               'genomics_england':{},
               'gwas_catalog':{},
               'intogen':{},
               'phenodigm':{},
               'phewas_catalog':{},
               'progeny':{},
               'reactome':{},
               'slapenrich':{},
               'sysbio':{},
               'uniprot':{},
               'uniprot_literature':{},
               'uniprot_somatic':{}}

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
df.to_csv("ot_metrics.csv", index=False)
