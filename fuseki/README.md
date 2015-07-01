# Fuseki (Jena)

Download Fuseki, start it and insert the schemes into it

  1. Download and unzip Fuseki into this directory (from: http://jena.apache.org/download/#apache-jena-fuseki)
     ... apache-jena-fuseki-2.0.0.zip (July 2015)
  2. Make a directory for your SKS database
     mkdir dbs
     mkdir dbs/sks 
  3. Go into the apache-jena-fuseki-* directory and run fuseki in the background (or in a separate shell)
     fuseki -
  4. Return to this directory and run the 'loadSchemes.sh' script in this directory

For more details, see the http://jena.apache.org/documentation

Then run drugRecipes.py
