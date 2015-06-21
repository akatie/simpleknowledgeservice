#!/usr/bin/env python

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it under the terms of 
# the GNU Affero General Public License version 3 (AGPL) as published by the Free Software 
# Foundation.
# (c) 2015 caregraf
#

import json
from datetime import datetime
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")
    
"""
TODO:
1. consider loading from .zip version of releases as faster? [and need to auto zip in maker!]
2. make sure mongo install works (Wikipedia) and gives relative sizes
   ... do a WikiInstall
"""

"""
First INSTALL MONGO: http://docs.mongodb.org/manual/installation/
Second create the database directory: dbs/sksdb

before running - start local server ...
> ./mongod --dbpath dbs/sksdb & 

Simple invoke: python datasetsToMongoDB.py
"""

MONGODBNAME = "sksdb"
DATABASE_DIR = "dbs/" + MONGODBNAME # strategy is one DB with collection per scheme
MONGODB_URI = 'mongodb://localhost' # :27017/smsdb
SCHEMES_DIR = "../schemes/"

SCHEMES = [
    "rxnorm",
    # "mthspl"
]

def datasetsToMongo():
    """
    Load available schemes one MongoDB database with one Collection per scheme
    """
    
    # REM: server must be started on params of MONGODB_URI
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        print '... is mongoDB running?'
        return

    db = client[MONGODBNAME]
    print "Using Mongo DB", db.name
    
    for i, schemeMN in enumerate(SCHEMES, 1):
    
        # purge current contents
        if schemeMN in db.collection_names():
            print "Purging contents of pre-existing", schemeMN, "collection"
            db[schemeMN].remove()
    
        schemeCollection = db[schemeMN] # identify collection with schemeMN
        
        schemeJLD = json.load(open(SCHEMES_DIR + schemeMN + "/" + schemeMN + ".json"))
        print "scheme JSON loaded - now inserting into Mongo ..."
    
        # @graph as ignoring context information in MongoDB
        descriptions = schemeJLD["@graph"]
        for i, description in enumerate(schemeJLD["@graph"], 1):
            # Use id as the _id in Mongo - avoids an extra index
            description["_id"] = description["id"]
            del description["id"]
        
        start = datetime.now()
        schemeCollection.insert(descriptions)
        print "Collection", schemeMN, "has", schemeCollection.count(), "members"
        print "Load of", len(descriptions), "of scheme", schemeMN, "took", datetime.now() - start
        print
    
    print "... done: Mongo stats now"
    print db.command("dbstats")
    print 
        
# ############################# Driver ####################################

def main():

    datasetsToMongo()
    
if __name__ == "__main__":
    main()
