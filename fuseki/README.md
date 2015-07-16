# Fuseki (Jena)

  1. Download and unzip Fuseki into this directory from http://jena.apache.org/download/#apache-jena-fuseki into this directory ...

     apache-jena-fuseki-2.0.0

  2. Run the 'importSchemes.sh' script. Will take a few minutes.

  3. In a new shell, go into the apache-jena-fuseki* directory and run fuseki

     fuseki-server --update --loc ../sksdb /sks

  4. To see queries in action, run 

     python drugRecipes.py 

