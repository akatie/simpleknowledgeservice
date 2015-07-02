# Fuseki (Jena)

  1. Download and unzip Fuseki into this directory (from: http://jena.apache.org/download/#apache-jena-fuseki)
     ... apache-jena-fuseki-2.0.0.zip (July 2015). Rename it to apache-jena-fuseki (ie/ no version information)

  2. Make a directory for your SKS database
 
     mkdir sksdb

  3. Run the 'loadSchemes.sh' script

  4. In a new shell, go into the apache-jena-fuseki-* directory and run fuseki

     fuseki-server --update --loc ../sksdb /sks

  5. Run 

     python drugRecipes.py 

     to see queries in action

