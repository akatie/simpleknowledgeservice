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
    
from importSchemes import MONGODBNAME, MONGODB_URI

"""
All schemes have one ConceptScheme description. It contains a
mixture of general and per version meta data about a scheme. This
set of routines will print out these details about the schemes
in a Simple Knowledge Service's MongoDB as well as walk down to 
the key organizing concepts ("Broader Tops") of the scheme.
"""

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

    schemes = sorted(db.collection_names(include_system_collections=False))   
    print "Schemes supported - one collection per scheme", schemes
    
    for schemeMN in schemes:
            
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
    
    # Unless a scheme is flat (it has no hierarchy), it will have two or more
    # "top concepts". These are the main organizing concepts of a scheme.
    # Examples include "Drug", "Dose Form" ... for RxNORM and "Clinical Finding", "Substance" for SNOMED).
    if "hasTopConcept" not in schemeDescription: # TODO: show random ex concept even though flat
        print "Flat, unstructured scheme - no topConcepts. Nothing more to report"
        print
        return
    
    topConceptIds = [c["id"] for c in schemeDescription["hasTopConcept"]]
    print
    print "\t-------------- Top Concepts", len(topConceptIds), "--------------"
    print "\t... the organizing concepts"
    for i, tConceptDescription in enumerate(schemeCollection.find({"_id": {"$in": topConceptIds}}).sort("numberActiveSubordinates", -1), 1):
        if i == 1: # most popular BT is the first as sorting
            mostPopularTId = tConceptDescription["_id"]
        print "\t", i, tConceptDescription["prefLabel"], "(" + tConceptDescription["_id"] + ")"
        print "\t\tChildren", tConceptDescription["numberActiveSubordinates"] 
                    
    """
    Let's display a child of the most popular broader top, one that hasn't been retired
    (deprecated). 
    
    All inactive/retired concepts with have the value 'true' for 'deprecated'. 
    Active concepts won't have a 'deprecated' field.
    
    If a scheme supports matches to other schemes then make sure the example is matched.
    """
    print 
    print "\t-------------- Example (Active) Concept --------------"
    findArgs = {"broaderTop.id": mostPopularTId, "deprecated" : { "$exists" : False }}
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
