# Fuseki (Jena)

  1. Download and unzip Fuseki into this directory (from: http://jena.apache.org/download/#apache-jena-fuseki)
     ... apache-jena-fuseki-2.0.0.zip (July 2015)

  2. Run the 'importSchemes.sh' script. Will take a few minutes but once loaded, you're ready to go.
     - it will install a database in a new or refreshed directory called 'sksdb'

  3. In a new shell, go into the apache-jena-fuseki* directory and run fuseki

     fuseki-server --update --loc ../sksdb /sks

  4. To see queries in action, run 

     python drugRecipes.py 

