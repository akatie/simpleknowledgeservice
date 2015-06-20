#!/usr/bin/env python

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it under the terms of 
# the GNU Affero General Public License version 3 (AGPL) as published by the Free Software 
# Foundation.
# (c) 2015 caregraf
#

import re 
import urllib, urllib2
import json
from datetime import datetime
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")

"""
INSTALL MONGO: http://docs.mongodb.org/manual/installation/

REM: before running - start local server ...
> ./mongod --dbpath dbs/smsdb & 

"""

MONGODBNAME = "smsdb"
DATABASE_DIR = "dbs/" + MONGODBNAME # strategy is one DB with collection per scheme
MONGODB_URI = 'mongodb://localhost' # :27017/smsdb

FMQLEP = "http://livevista.caregraf.info/fmqlEP" # Endpoint address of Caregraf demo VistA

# Just getting data of patient 9 from CG Demo system
QUERIES_FOR_DATA = [
    {"label": "Record of Patient 9", "id": "2-9"},
    {"label": "Vitals since 2008 of Patient 9", "type": "120_5", "filter": ".02=2-9&.01>2008-04-01"},
    {"label": "Problems of Patient 9", "type": "9000011", "filter": ".02=9000001-9"},
    {"label": "Prescriptions of Patient 9", "type": "52", "filter": "2=2-9"}
]

def datasetsToMongo():
    """
    Send a series of FMQL queries for a patient and store the results in Mongo
    """

    # Check to ensure don't try to install data twice
    
    # REM: server must be started on params of MONGODB_URI
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        print '... is mongoDB running?'
        return

    db = client[MONGODBNAME]
    print "Using Mongo DB", db.name
    
    for i, queryInfo in enumerate(QUERIES_FOR_DATA, 1):
        if "id" in queryInfo:
            fileType = queryInfo["id"].split("-")[0]
            query = "DESCRIBE " + queryInfo["id"] + " CSTOP 1000"
        else:
            fileType = queryInfo["type"]
            query = "DESCRIBE " + fileType + " FILTER(" + queryInfo["filter"] + ")" + " CSTOP 1000"
        print
        print "Sending FMQL query", query
        query = {"fmql": query, "format": "JSON-LD"}
        queryURL = FMQLEP + "?" + urllib.urlencode(query)
        jreply = json.loads(urllib2.urlopen(queryURL).read())
        if jreply.has_key("error"):
            print "Got error %s during FMQL query - exiting" % jreply["error"]
            return
        descriptions = jreply["@graph"]
        print "Query", i, "returned", len(descriptions), "all of type", fileType
    
        # purge current contents
        if fileType in db.collection_names():
            print "Purging contents of pre-existing", fileType, "collection"
            db[fileType].remove()
    
        ftCollection = db[fileType] # identify collection with VistA FileType ie/ mirror FileMan's data layout
    
        # Use id as the _id in Mongo - avoids an extra index
        # TODO: will add scoped name for the VistA (ie site id of the VistA into its id)
        # ex/ "id" ... visn0044:50-1 etc.
        for i, description in enumerate(descriptions, 1):
            description["_id"] = description["id"]
            del description["id"]
        
        start = datetime.now()
        ftCollection.insert(descriptions)
        print "Collection", fileType, "has", ftCollection.count(), "members"
        print "Load of", len(descriptions), "of type", fileType, "took", datetime.now() - start
        print
    
    print "... done: Mongo stats now"
    print db.command("dbstats")
    print 
        
# ############################# Demo Driver ####################################

def main():

    datasetsToMongo()
    
if __name__ == "__main__":
    main()
