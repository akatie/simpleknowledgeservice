#!/usr/bin/env python
# -*- coding: utf8 -*- 

#
# LICENSE:
# This program is free software; you can redistribute it and/or modify it under the terms of 
# the GNU Affero General Public License version 3 (AGPL) as published by the Free Software 
# Foundation.
# (c) 2015 caregraf
#

import re 
import json
from datetime import datetime
try:
    from pymongo import MongoClient
except:
    raise Exception("You must install the package pymongo - http://api.mongodb.org/python/current/installation.html")
    
from importSchemes import MONGODBNAME, SCHEMES

"""
All schemes have one ConceptScheme description. It contains a
mixture of general and per version meta data about a scheme. This
set of routines will print out these details about the schemes
in a Simple Knowledge Service's MongoDB as well as walk down to 
the key organizing concepts ("Broader Tops") of the scheme.
"""

MONGODB_URI = 'mongodb://localhost' # :27017/sksdb 

def reportSchemes():

    # REM: server must be started on params of MONGODB_URI
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        return

    print
    print "======= Report on Contents of MongoDB", MONGODBNAME, "========"

    print
    db = client[MONGODBNAME]
    print "Simple Knowledge Service DB:", db.name
    
    print "Schemes supported - one collection per scheme", db.collection_names(include_system_collections=False)
    
    if len(db.collection_names(include_system_collections=False)) < len(SCHEMES):
        raise Exception("Did you run importSchemes.py? Wrong number of collections in db - exiting")
        
    for schemeMN in SCHEMES:
            
        reportScheme(db, schemeMN)
    
def reportScheme(db, schemeMN):
    """
    Only interested in the ConceptScheme resource, the one with id
            <schemeMN>:scheme
    It contains a mixture of meta data about a particular version of a scheme
    """
    useCollection = schemeMN
    schemeCollection = db[useCollection] 
    
    schemeDescription = schemeCollection.find_one({"_id": schemeMN + ":scheme"})
    
    # Leaving out "umlsCUI", "referencedSchemes", "hasTopConcept", "sourceFormat"
    print
    print schemeDescription["prefLabel"], "(" + schemeDescription["_id"] + ")"
    print "\tTotal 'documents' (by MongoDB):", schemeCollection.count()
    
    print
    print "\t-------------- details --------------"    
    if "definition" in schemeDescription:
        print "\tDefinition:"
        print "\t\t", schemeDescription["definition"]
    print "\tVersion:", schemeDescription["version"]
    print "\tLast update:", schemeDescription["lastUpdate"]
    print "\tCopyright:"
    print "\t\t", schemeDescription["copyright"]
    
    print
    print "\t-------------- statistics --------------"
    # Statistics are from the VoID schema (http://www.w3.org/TR/void/) and Caregraf 
    # additions. Some include ...
    STAT_PREDS = [("void:distinctSubjects", "Subjects"), ("void:triples", "Total Assertions"), ("cgkos:literalTriples", "Property Assertions"), ("cgkos:edgeTriples", "Graph Assertions"), ("cgkos:matched", "Matches"), ("cgkos:broaderTops", "Topmost (Broader Top) Concepts")]
    for predInfo in STAT_PREDS:
        if predInfo[0] not in schemeDescription:
            continue
        print "\t" + predInfo[1] + ":", schemeDescription[predInfo[0]]
    
    # Unless a scheme is flat (it has no hierarchy) then it will have one topConcept
    # and one or more second level concepts. In these scheme representations, such
    # second level concepts are called "broader tops". These are the main organizing
    # concepts of a scheme ("Drug", "Dose Form" ... for RxNORM) or ("Clinical Finding", "Substance" for SNOMED).
    print
    print "\t-------------- Broader Tops --------------"
    print "\t... the organizing concepts"
    topConceptId = schemeDescription["hasTopConcept"]["id"]
    for i, btConceptDescription in enumerate(schemeCollection.find({"broader.id": topConceptId}, {"prefLabel": 1, "numberSubordinates": 1}).sort("numberSubordinates", -1), 1):
        if i == 1: # most popular BT is the first as sorting
            mostPopularBTId = btConceptDescription["_id"]
        print "\t", i, btConceptDescription["prefLabel"], "(" + btConceptDescription["_id"] + ")"
        print "\t\tChildren", btConceptDescription["numberSubordinates"] 
     
    """
    Let's display a child of the most popular broader top, one that hasn't been retired
    (deprecated). 
    
    All inactive/retired concepts with have the value 'true' for 'deprecated'. 
    Active concepts won't have a 'deprecated' field.
    
    If a scheme supports matches to other schemes then make sure the example is matched.
    """
    print 
    print "\t-------------- Example (Active) Concept --------------"
    if "cgkos:matched" in schemeDescription:
        findArgs = {"broadMatch": {"$exists": True}}
    else:   
        findArgs = {"broaderTop.id": mostPopularBTId, "deprecated" : { "$exists" : False }}
    exampleConceptDescription = schemeCollection.find_one(findArgs)
    schemePreds = []
    print "\t", exampleConceptDescription["prefLabel"], "(" + exampleConceptDescription["_id"] + ")"
    print
    for pred in exampleConceptDescription:
        if pred in ["_id", "prefLabel"]:
            continue
        if re.search(r':', pred):   
            schemePreds.append(pred)
            continue # just show generic, non scheme properties first
        print "\t", pred, exampleConceptDescription[pred]
    print
    for pred in schemePreds:
        print "\t", pred, exampleConceptDescription[pred]
    print
        
# ############################# Driver ####################################

def main():

    reportSchemes()
    
if __name__ == "__main__":
    main()
