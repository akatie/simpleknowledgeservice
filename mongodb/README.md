# Use MongoDB for a Simple (Medical) Knowledge Service

  1. Install MongoDB ([see](http://docs.mongodb.org/manual/installation/)) and its Python Package ([see](http://api.mongodb.org/python/current/installation.html))

  2. Make a directory for your database called `sksdb` ...

         mkdir sksdb

  3. In a new shell, start Mongo and point it to the database directory

         mongod --dbpath sksdb & 

  4. (Re)load schemes

         python importSchemes.py

     ... sample output in _README_OUTPUT_IMPORTSCHEMES_

  5. To see queries in action, run ...

         python reportSchemes.py

     and

         python drugRecipes.py

     ... sample outputs are in _README_OUTPUT_REPORTSCHEMES_ and _README_OUTPUT_DRUGRECIPLES_
