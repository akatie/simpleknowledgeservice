#!/bin/bash
echo
DBLOC=sksdb
mkdir -p $DBLOC
echo "On $(date +%Y/%m/%d), clearing '${DBLOC}' and (re)loading schemes ..."
if [ "$(ls -A $DBLOC)" ]; then
    echo "Clearing current contents of database location '$DBLOC'"
    rm $DBLOC/*
fi
SCHEMEZIPS="../schemes/*zip"
ZIPRE='\/([A-Z0-9]+)_([^\.]+)\.zip$'
CP=".:apache-jena-fuseki/fuseki-server.jar"
for szip in $SCHEMEZIPS; do
    if [[ $(echo $szip) =~ $ZIPRE ]]; then
        SCHEMEMN=${BASH_REMATCH[1]}
        GRAPHID="http://schemes.caregraf.info/$(tr [A-Z] [a-z] <<< "$SCHEMEMN")"
        VERSION=${BASH_REMATCH[2]}
        echo 
        echo "Loading ${SCHEMEMN}, version ${VERSION} into <${GRAPHID}> ..."
        for i in {1..100}
        do
            echo -n '-'
        done
        echo
        TTLINZIP="${SCHEMEMN}_${VERSION}/scheme.ttl"
        echo $TTLINZIP
        unzip -p $szip $TTLINZIP | java -cp $CP riotcmd.turtle --output nquads | java -cp $CP tdb.tdbloader --loc $DBLOC --graph $GRAPHID -- -
    fi
echo
echo
done
