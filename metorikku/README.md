# Platform data metrics

OpenTargets ETL pipeline to generate metrics for all data releases, evidences and associations

### Requirements

1. Java 1.8
2. https://github.com/YotpoLtd/metorikku
3. assocations and evidences from data release

### Run the scala script

In order to run the script you might want to update the input path entries from `platform.yaml` file.

```sh
export JAVA_OPTS="-Xms512m -Xmx<mostofthememingigslike100G>"
# to compute the dataset
java -Dspark.master=local[*] -Dspark.sql.broadcastTimeout=60000 -Dspark.executor.heartbeatInterval=60000 -Dspark.sql.crossJoin.enabled=true -Dspark.driver.maxResultSize=0 -cp metorikku-standalone.jar com.yotpo.metorikku.Metorikku -c platform.yaml
```

# Copyright
Copyright 2014-2018 Biogen, Celgene Corporation, EMBL - European Bioinformatics Institute, GlaxoSmithKline, Takeda Pharmaceutical Company and Wellcome Sanger Institute

This software was developed as part of the Open Targets project. For more information please see: http://www.opentargets.org

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
