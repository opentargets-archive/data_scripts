#################################################
## 
## Purpose of script: Parse Probe Miner data dump to be used as target annotation in Open Targets
## Description: Process Probe Miner data dump and generate a tsv file with three columns:
##              HGNC symbol, Uniprot accession and Nr of probes 
##
## Authors: Michaela Spitzer, Asier Gonzalez
## Maintainer: Asier Gonzalez
## Email: "data@opentargets.org
##
## Date Created: Oct 2018
##
## Copyright: Copyright 2014-2019, Open Targets
## License: Apache 2.0
##
#################################################

# Work on directory with input file
working_dir <- file.path("/Users","gonzaleza","opentargets", "19.09")
setwd(working_dir)

# Specify input file
probe_miner_dump <- "probeminer_datadump_2018-09-19.txt"

# *** Get a map of uni_prot - hgnc_symbol via biomaRt ***
library('biomaRt')
ensembl <- useMart('ensembl', dataset="hsapiens_gene_ensembl")
ID <- getBM(attributes = c("hgnc_symbol", "uniprot_gn"),mart=ensembl)


# *** Load and process the Probe Miner data ***
#D<-read.table(file="probeminer_datadump_2018-05-01.txt", header=TRUE, sep="\t", stringsAsFactors=FALSE)
# Need to add comment.char="" because the smile strings can contain '#' 
D<-read.table(file= probe_miner_dump, header=TRUE, sep="\t", stringsAsFactors=FALSE, comment.char="")
# Pull out target and probe IDs with target_potency_raw > 5 to generate a 'count table'
D2<-D[D[,15]>5,1:2] # Get number of unique targets and probes: length(unique(D2[,2])) & length(unique(D2[,1]))
# Generate the 'count/frequency table'
D3<-table(D2[,1])
# Map provided UniProt IDs to HGNC symbols in D4
D4 <- cbind(cbind(names(D3), D3), rep("", times=length(D3)))
colnames(D4)<-c("uniprot_symbol", "nr_of_probes", "hgnc_symbol")
for (i in 1:nrow(D4)){
	D4[i,3] <- ID[match(D4[i,1], ID[,2]),1]
}

# Get the unmapped IDs
tmp<-D4[is.na(D4[,3]),]
# Export unmapped IDs and process CSV file in Google sheet 'ProbeMiner - ID Mapping'
write.csv(tmp, file="ProbeMiner_manualMapping_2.csv")
# Get all targets that have been mapped
pm_1810<-D4[!is.na(D4[,3]),]  
# Read in targets with manually curated hgnc symbols 
pm_manual<-as.matrix(read.csv(file="ProbeMiner - ID Mapping - Final Mapping Oct 2018.csv", 
	header=TRUE, stringsAsFactors=FALSE))
# Combine both sets of targets
pm_1810_2<-rbind(pm_1810, pm_manual)
# Save table with hgnc_symbol, uniprot_symbol, nr_of_probes for the OT pipeline
write.table(pm_1810_2[,c(3,1,2)], file="chemicalprobes_probeminer_20181015.tsv", sep="\t", row.names=FALSE, quote=FALSE) 

### --- End of Probe Miner data dump preprocessing ---


### --------------------------------------------------------------------------------------
### Optional: overlap with targets that have manually curated probes ###
hist(table(D[D[,18]==1,1]), breaks=200, ylim=c(0,50))

# List of proteins that have manually curated chemical probes
OTprobeTargets<-read.table(file="uniprot-yourlist%3AM20180716A7434721E10EE6586998A056CCD0537E9345E6M-filtered-rev--.tab", stringsAsFactors=FALSE, sep="\t", header=TRUE)

setdiff(OTprobeTargets[,3],unique(D[,1]))
# Targets covered by manually curated probes, but not ProbeMiner
setdiff(unique(OTprobeTargets[,3]),unique(D[D[,18]==1,1])) # 143
# Targets covered by ProbeMiner but not by manually curated probes
setdiff(unique(D[D[,18]==1,1]), unique(OTprobeTargets[,3])) # 207


# 50 Uniprot IDs overlap between manually curated chemical probes and Probe Miner sets
intersect(unique(OTprobeTargets[,3]), (unique(D[D[,18]==1,1])))

# Get the number of 'suitable probes' per target
sort(table(suitableProbes[,1]))
### End: optional ###