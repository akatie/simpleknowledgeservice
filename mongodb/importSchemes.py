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
import re
from zipfile import ZipFile
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")

"""
Before running:
- INSTALL MongoDB from http://docs.mongodb.org/manual/installation/ and its Python package, pyMongo from http://api.mongodb.org/python/current/installation.html
- create the database directory 'sksdb'
- run Mongo:
  > mongod --dbpath sksdb & 

TODO:
- more on sizing of raw scheme vs MongoDB representation
"""

MONGODBNAME = "sksdb" # will exist as can't start mongod otherwise
DATABASE_DIR = MONGODBNAME # strategy is one DB with collection per scheme
MONGODB_URI = 'mongodb://localhost' # :27017/smsdb
SCHEMES_DIR = "../schemes/"

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
    
    # Assemble schemes per scheme
    schemeZipFiles = [zipFile for zipFile in os.listdir(SCHEMES_DIR) if re.match(r'[A-Z\d]+_.+\.zip$', zipFile)]
    if not len(schemeZipFiles):
        raise Exception("No schemes in schemes directory. Why not download some. Exiting ...")
    schemeZipsBySchemeMN = {}
    for zipFile in schemeZipFiles:
        schemeMN = zipFile.split("_")[0].lower()
        if schemeMN in schemeZipsBySchemeMN:
            raise Exception("> 1 version for scheme " + schemeMN + " in schemes directory. Only allowed one version per scheme. Exiting ...")
        schemeZipsBySchemeMN[schemeMN] = zipFile
    
    for i, (schemeMN, schemeZipFile) in enumerate(schemeZipsBySchemeMN.iteritems(), 1):
    
        print "Loading scheme", schemeMN, "from", schemeZipFile
    
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
