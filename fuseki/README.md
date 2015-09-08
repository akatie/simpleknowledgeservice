# Use Fuseki (Jena) for an SKS

  1. Download the Fuseki zip from its [download page](http://jena.apache.org/download/#apache-jena-fuseki) and unzip it here ...

         apache-jena-fuseki-2.3.0 (version is 2.3.0 at time of writing)

     Fuseki 2.3.0 requires Java 1.8+. Run java -version to make sure your Java is up to date. If it's not, you can download the latest
     version from [Oracle's site](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

  2. Run the 'importSchemes.sh' script. It takes a few minutes ...

         ./importSchemes.sh

     ... a sample output is in _README_OUTPUT_IMPORTSCHEMES_

  3. In a new shell, go into the apache-jena-fuseki* directory and run fuseki

         cd apache-jena-fuseki-2.3.0
         ./fuseki-server --update --loc ../sksdb /sks
                   or
         ./fuseki-server --loc ../sksdb --set tdb:unionDefaultGraph=true /sks (easy cross graph querying)

  4. To see queries in action, run ...

         python drugRecipes.py 

     ... a sample output is in _README_OUTPUT_DRUGRECIPLES_

