# Fuseki (Jena)

Download Fuseki, start it and insert the schemes into it

  1. Download and unzip Fuseki into this directory (from: http://jena.apache.org/download/#apache-jena-fuseki)
     ... apache-jena-fuseki-2.0.0.zip (July 2015)
  2. Make a directory for your SKS database
     mkdir dbs
     mkdir dbs/sks 
  3. Run the 'loadSchemes.sh' script in this directory
  4. Go into the apache-jena-fuseki-* directory and run fuseki (in the background or do in a separate shell)
     fuseki-server --update --loc /....../dbs/sksdb /sks &
  5. Run python drugRecipes.py to see queries in action

For more details, see the http://jena.apache.org/documentation
