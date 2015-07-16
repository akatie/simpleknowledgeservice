#!/usr/bin/env python
# -*- coding: utf8 -*- 

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it under the terms of 
# the GNU Affero General Public License version 3 (AGPL) as published by the Free Software 
# Foundation.
# (c) 2015 caregraf
#

import os
import json
from datetime import datetime
from zipfile import ZipFile
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")

"""
First INSTALL MONGO: http://docs.mongodb.org/manual/installation/
Second create the database directory: dbs/sksdb

before running - start local server ...
> mongod --dbpath dbs/sksdb & 

Then invoke: ./importSchemes.py

TODO:
- more on sizing of raw scheme vs MongoDB representation
- warnings on zip scheme size ie/ will take time to load ... do ....
"""

MONGODBNAME = "sksdb"
DATABASE_DIR = "dbs/" + MONGODBNAME # strategy is one DB with collection per scheme
MONGODB_URI = 'mongodb://localhost' # :27017/smsdb
SCHEMES_DIR = "../schemes/"

SCHEMES = [
    "rxnorm",
    "mthspl"
]

def importSchemes():
    """
    Load available schemes one MongoDB database with one Collection per scheme
    """
    
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        print '... is mongoDB installed and running at', MONGODB_URI
        return

    db = client[MONGODBNAME]
    print "Using Mongo DB", db.name
    
    for i, schemeMN in enumerate(SCHEMES, 1):
    
        print "Loading latest version of scheme", schemeMN
    
        # Identify the latest version of this scheme - should be in a zip in SCHEMES_DIR
        schemeZipFiles = [zipFile for zipFile in os.listdir(SCHEMES_DIR) if zipFile.lower().startswith(schemeMN) and zipFile.endswith(".zip")]
        if len(schemeZipFiles) != 1:
            raise Exception("Can't import version of scheme " + schemeMN + " as either missing or there is more than one")
        schemeZipFile = schemeZipFiles[0]
    
        # purge current contents
        if schemeMN in db.collection_names():
            print "\tpurging contents of pre-existing MongoDB collection", schemeMN
            db[schemeMN].remove()
    
        schemeCollection = db[schemeMN] # identify collection with schemeMN
        
        # Loading JSON before inserting as want to change it a little for MongoDB
        # ... this looks convoluted but it's the usual zipFile/file io stuff
        print "\tloading latest scheme JSON from zip file", schemeZipFile, "..."
        schemeJLD = json.load(ZipFile(SCHEMES_DIR + schemeZipFile, "r").open(schemeZipFile.split(".")[0] + "/" + "scheme.jsonld"))
            
        # @graph as ignoring context information in MongoDB
        descriptions = schemeJLD["@graph"]
        for i, description in enumerate(schemeJLD["@graph"], 1):
            # Use id as the _id in Mongo - avoids an extra index
            description["_id"] = description["id"]
            del description["id"]
        print "\tscheme JSON loaded and changed - now inserting into Mongo ..."
        
        start = datetime.now()
        schemeCollection.insert(descriptions)
        print "\tCollection", schemeMN, "has", schemeCollection.count(), "members"
        print "\tLoad of", len(descriptions), "resources of scheme", schemeMN, "took", datetime.now() - start
        print
    
    print "... done: Mongo stats now"
    print db.command("dbstats")
    print
    print "... why not run ./reportScheme.py for reports on the loaded schemes"
    print 
        
# ############################# Driver ####################################

def main():

    importSchemes()
    
if __name__ == "__main__":
    main()
