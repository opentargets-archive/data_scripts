ulimit -c unlimited
export JAVA_OPTS="-Xms1G -Xmx200G"
java -Dspark.master=local[*] -Dspark.driver.maxResultSize=0 -cp metorikku-standalone.jar com.yotpo.metorikku.Metorikku -c platform.yaml
