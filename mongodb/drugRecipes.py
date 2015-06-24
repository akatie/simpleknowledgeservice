#!/usr/bin/env python

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
    
from importSchemes import MONGODBNAME

"""
Example queries on drug schemes
"""

MONGODB_URI = 'mongodb://localhost' # :27017/sksdb 

def runRecipes():
        
    # REM: server must be started on params of MONGODB_URI
    try:
        client = MongoClient(MONGODB_URI)
    except Exception, err:
        print 'Error: %s' % err
        return

    print
    print "======= Running Drug Recipes on Contents of MongoDB", MONGODBNAME, "========"

    print
    db = client[MONGODBNAME]
    print "Simple Knowledge Service DB:", db.name
    
    rxnormLookupByName(db)
    rxnormBrandToGeneric(db)
    
    ndcCodeToRxNORMCode(db)
    
def rxnormLookupByName(db):
    """
    Simple stuff - lookup by name, grouping by type
    """
    rxnormCollection = db["rxnorm"] 

    # Lookup every 'Esomeprazole' concepts for their ids, names and types. Order by type.
    INGREDIENT_LABEL = "Esomeprazole"
    conceptDescriptions = rxnormCollection.find({"prefLabel": {'$regex':'^' + INGREDIENT_LABEL}}, {"prefLabel": 1, "broaderTop": 1}).sort("broaderTop.id", -1)
    currentBT = ""
    print
    print "Looking up Concepts with", INGREDIENT_LABEL, "in their names ..."
    for i, conceptDescription in enumerate(conceptDescriptions, 1):
        if conceptDescription["broaderTop"]["id"] != currentBT:
            currentBT = conceptDescription["broaderTop"]["id"]
            print 
            currentBTLabel = rxnormCollection.find_one({"_id": currentBT}, {"prefLabel": 1})["prefLabel"]
            print "\tType:", currentBTLabel, "(" + currentBT + ")"
        print "\t\t", i, conceptDescription["prefLabel"], "(" + conceptDescription["_id"] + ")"
    print
        
def rxnormBrandToGeneric(db):
    """
    RxNORM has separate concepts/codes for the branded version of a drug and its
    generic but very often you wish to reduce the brand to its generic.
    """
    rxnormCollection = db["rxnorm"] 
    
    EXAMPLE_BRAND = "rxnorm:606728" # Nexium 20mg Tablet
    
    brandDescription = rxnormCollection.find_one({"_id": EXAMPLE_BRAND})
    print
    print "Go from Brand to Generic RXNORM ..."
    print "\tGoing from brand", brandDescription["prefLabel"], "(" + brandDescription["_id"] + ")"
    # use the 'tradename_of' relationship
    print "\tusing <tradename_of> which has a value of", brandDescription["rxnormo:tradename_of"]
    
    genericDescription = rxnormCollection.find_one({"_id": brandDescription["rxnormo:tradename_of"]["id"]})
    print "\tgot us to", genericDescription["prefLabel"], "(" + genericDescription["_id"] + ")" 
    print
    
    # Note that needed two steps as this normalized "graph" JSON doesn't have a
    # filterable 'has_tradename' relationship. 
    
def ndcCodeToRxNORMCode(db):
    """
    Key: full NDC codes represent packages but RxNORM represents drug products. When
    we match from NDC code to RxNORM code, we first traverse within the MTHSPL scheme
    from package to product and then get the product's RxNORM match.
    
    ie/
        Package --[packaging_of]--> Product --[broadMatch]--> RxNORM Drug (SBD/SCD)
    """    
    mthsplCollection = db["mthspl"]     
    
    CODE = "0186-5020-82" # 20MG Esomeprazole
    packageWithCode = mthsplCollection.find_one({"code": CODE}, {"prefLabel": 1, "mthsplo:packaging_of": 1})
    print 
    print "From NDC Code to RxNORM Code"
    print "\tCODE", CODE, "identifies a packaging of", packageWithCode["prefLabel"], "(" + packageWithCode["_id"] + ")"
    productOfPackage = mthsplCollection.find_one({"_id": packageWithCode["mthsplo:packaging_of"]["id"]}, {"broadMatch": 1})
    print "\tIts products matches the RxNORM concept with id", productOfPackage["broadMatch"]
    
    rxnormCollection = db["rxnorm"]
    rxnormMatch = rxnormCollection.find_one({"_id": productOfPackage["broadMatch"][0]["id"]}, {"prefLabel": 1, "code": 1, "broaderTop": 1})
    print "\tThat is RxNORM Concept", rxnormMatch["prefLabel"], "of type", rxnormMatch["broaderTop"]["id"]
    print "\tand code", rxnormMatch["code"]
    print
    
# ############################# Driver ####################################

def main():

    runRecipes()
    
if __name__ == "__main__":
    main()

