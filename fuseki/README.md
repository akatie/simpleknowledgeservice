# Use Fuseki (Jena) for an SKS

  1. Download the Fuseki zip from its [download page](http://jena.apache.org/download/#apache-jena-fuseki) and unzip it here ...

         apache-jena-fuseki-2.0.0

     ... fuseki is `2.0.0` at the time of writing.

  2. Run the 'importSchemes.sh' script. It takes a few minutes ...

         ./importSchemes.sh

     ... a sample output is in _README_OUTPUT_IMPORTSCHEMES_

  3. In a new shell, go into the apache-jena-fuseki* directory and run fuseki

         cd apache-jena-fuseki-2.0.0
         ./fuseki-server --update --loc ../sksdb /sks

  4. To see queries in action, run ...

         python drugRecipes.py 

     ... a sample output is in _README_OUTPUT_DRUGRECIPLES_

