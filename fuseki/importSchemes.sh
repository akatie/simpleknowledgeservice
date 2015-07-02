#
# Load available schemes
# 
# Reads from zip, pipes through an nquads convertor and then imports into 
# named graph
# 
# For more on Jena i/o read https://jena.apache.org/documentation/io/
#
# TODO: loop schemes inferring schemeMN and graph from naming convention  
#

unzip -p ../schemes/RXNORM_15AA_150601F.zip RXNORM_15AA_150601F/scheme.ttl | java -cp ".:apache-jena-fuseki/fuseki-server.jar" riotcmd.turtle --output nquads | java -cp ".:apache-jena-fuseki/fuseki-server.jar" tdb.tdbloader --loc sksdb --graph http://schemes.caregraf.info/rxnorm -- -
unzip -p ../schemes/MTHSPL_2015_05_22.zip MTHSPL_2015_05_22/scheme.ttl | java -cp ".:apache-jena-fuseki/fuseki-server.jar" riotcmd.turtle --output nquads | java -cp ".:apache-jena-fuseki/fuseki-server.jar" tdb.tdbloader --loc sksdb --graph http://schemes.caregraf.info/mthspl -- -