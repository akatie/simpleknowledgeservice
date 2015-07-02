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
import urllib, urllib2
    
"""
Example queries on drug schemes

These SPARQL based Jena examples match the drugRecipes for MongoDB 
"""

FUSEKI_QUERY_URI = "http://localhost:3030/sks/query"

def runRecipes():
        
    print
    print "======= Running Drug Recipes on Contents of Fuseki at", FUSEKI_QUERY_URI, "========"
    
    rxnormLookupByName()
    
    rxnormBrandToGeneric()
        
    ndcCodeToRxNORMCode()
        
def rxnormLookupByName():
    """
    Simple stuff - lookup by name, grouping by type
    
    Shows nature of SPARQL querying:
    
    1. Each scheme is in its own 'graph' and we query within that graph
    
    2. literal string lookup is slower than MongoDB
       - generic SPARQL doesn't promote very efficient literal (string) based lookup
       - but Jena does support string search capabilities with SPARQL extensions
       and will show these soon (https://jena.apache.org/documentation/query/text-query.html)
       
    3. the native SPARQL JSON is "fat" but clear ...
       - id: {"value": "...", "type": "uri"}
       - literal (string/boolean/int ...): {"value": "...", "type": "literal"}
       and though it returns full URIs (ex/ http://schemes.caregraf.info/rxnorm/..."),
       we can easily change these a namespaced form (ex/ rxnorm:...). We do this
       in the function 'sciURIToNSForm' defined below
       
    4. it is easy to reach down to get the label of an id inside one query. 
        - ?broaderTop skos:prefLabel ?broaderTopLabel
    """

    # Lookup every 'Esomeprazole' concepts for their ids, names and types. Order by type.    
    QUERY_ESOMEPRAZOLE_RXNORM_CONCEPTS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX cgkos: <http://schemes.caregraf.info/ontology#>
    SELECT DISTINCT ?id ?prefLabel ?broaderTop ?broaderTopLabel
    WHERE {GRAPH <http://schemes.caregraf.info/rxnorm> {
        ?id a skos:Concept ;
            skos:prefLabel ?prefLabel ;
            cgkos:broaderTop ?broaderTop .
        ?broaderTop skos:prefLabel ?broaderTopLabel .
        FILTER regex(?prefLabel, "Esomeprazole", "i")
    }}
    ORDER BY ?broaderTopLabel
    """
    print
    print "Looking up Concepts with Esomeprazole in their names ..."    
    print "... slower than MongoDB to do broad string searches ..."
    print
    print "Running query"
    print QUERY_ESOMEPRAZOLE_RXNORM_CONCEPTS
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": QUERY_ESOMEPRAZOLE_RXNORM_CONCEPTS, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    
    print "Results:"
    currentBTL = ""
    for i, binding in enumerate(reply["results"]["bindings"], 1):
    
        if currentBTL != binding["broaderTopLabel"]["value"]:
            currentBTL = binding["broaderTopLabel"]["value"]
            print
            print "\tType:", currentBTL, "(" + sciURIToNSForm(binding["broaderTop"]["value"]) + ")"
            
        print "\t\t", i, binding["prefLabel"]["value"] + " (" + sciURIToNSForm(binding["id"]["value"]) + ")"
    print
        
def rxnormBrandToGeneric():
    """
    RxNORM has separate concepts/codes for the branded version of a drug and its
    generic but very often you wish to reduce the brand to its generic.
    """

    print "Go from Brand to Generic RXNORM ..."
    print "-----------------------------------"
    
    EXAMPLE_BRAND_ID = "rxnorm:606728" # Nexium 20mg Tablet
    
    # In one step get the label of this branded drug id, the generic
    # equivalent (via the "tradename_of" relationship) and the label
    # of that generic.
    QUERY_RXNORM_FROM_BRAND_TO_GENERIC = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rxnorm: <http://schemes.caregraf.info/rxnorm/>
    PREFIX rxnormo: <http://schemes.caregraf.info/rxnormo/>
    SELECT DISTINCT ?brandLabel ?genericId ?genericLabel
    WHERE {GRAPH <http://schemes.caregraf.info/rxnorm> {
            %s skos:prefLabel ?brandLabel ;
                rxnormo:tradename_of ?genericId .
            ?genericId skos:prefLabel ?genericLabel
    }}
    """
    print
    query = QUERY_RXNORM_FROM_BRAND_TO_GENERIC % EXAMPLE_BRAND_ID
    print "Running query"
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    binding = reply["results"]["bindings"][0]
    print
    print "Result:"
    print "\tFrom:", binding["brandLabel"]["value"] + " (" + EXAMPLE_BRAND_ID + ")"
    print 
    print "\t\t", "using 'rxnormo:tradename_of' relationship ..."
    print
    print "\tTo:", binding["genericLabel"]["value"] + " (" + sciURIToNSForm(binding["genericId"]["value"]) + ")"
    print
    
def ndcCodeToRxNORMCode():
    """
    Key: full NDC codes represent packages but RxNORM represents drug products. When
    we match from NDC code to RxNORM code, we first traverse within the MTHSPL scheme
    from package to product and then get the product's RxNORM match.
    
    ie/
        Package --[packaging_of]--> Product --[broadMatch]--> RxNORM Drug (SBD/SCD)

    We can do one cross graph query, going from package code to details on RxNORM 
    concept in one query. We use propertypaths, a SPARQL 1.1 feature that let's us
    hop two steps easily.
    """    
    
    print "Go from NDC Code to RXNORM ..."
    print "------------------------------"
    
    CODE = "0186-5020-82" # 20MG Esomeprazole
    
    """
    Here we use a property path (http://www.w3.org/TR/sparql11-query/#propertypaths)
    
            mthsplo:packaging_of/skos:broadMatch ?rxnormMatchId .
            
    which skips an uninteresting intermediate (product) node. We could have been more
    long winded and used ...
    
                    mthsplo:packaging_of ?productId .
            ?productId skos:broadMatch ?rxnormMatchId .    
    """
    QUERY_RXNORM_MATCH_OF_PACKAGE_WITH_CODE = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX cgkos: <http://schemes.caregraf.info/ontology#>
    PREFIX mthsplo: <http://schemes.caregraf.info/mthsplo/>
    SELECT DISTINCT ?packageId ?packageLabel ?rxnormMatchId ?rxnormLabel ?rxnormBroaderTop ?rxnormCode
    FROM <http://schemes.caregraf.info/mthspl>
    FROM <http://schemes.caregraf.info/rxnorm>
    WHERE {
            ?packageId cgkos:code "%s" ;
                    skos:prefLabel ?packageLabel ;
                    mthsplo:packaging_of/skos:broadMatch ?rxnormMatchId .
            ?rxnormMatchId skos:prefLabel ?rxnormLabel ;
                    cgkos:broaderTop ?rxnormBroaderTop ;
                    cgkos:code ?rxnormCode  
    }
    """
    print
    print "Running query"
    query = QUERY_RXNORM_MATCH_OF_PACKAGE_WITH_CODE % CODE
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    mbindings = reply["results"]["bindings"] # only expect one match
    if len(mbindings) != 1:
        raise Exception("Expected one and only one RxNORM match for " + CODE)
    mbinding = mbindings[0]
    print
    print "Result:"
    print "\tFrom:", mbinding["packageLabel"]["value"] + " (" + sciURIToNSForm(mbinding["packageId"]["value"]) + ")", "code", CODE
    print
    print "\t\t", "via 'packaging_of' relation and then a match relation (2 steps) ..."
    print
    print "\tTo:", mbinding["rxnormLabel"]["value"] + " (" + sciURIToNSForm(mbinding["rxnormMatchId"]["value"]) + ")", "code", mbinding["rxnormCode"]["value"], "type", sciURIToNSForm(mbinding["rxnormBroaderTop"]["value"])
    print
    
    # rxnorm:SBD (Branded Drug) tells us that this is a branded drug and that
    # we could do an extra step and go from the code to the appropriate generic RxNORM.
    # This would add the logic of 'rxnormBrandToGeneric' 
    
def sciURIToNSForm(uri):
    """
    Pretty-ups most concept URIs by replacing full expansion with namespaced form.
    
    Ex/ http://schemes.caregraf.info/rxnorm/scheme -> rxnorm:scheme 
    """
    if not re.match(r'http', uri):
        return uri
    if not re.search(r'schemes\.caregraf\.info', uri):
        return uri
    return re.sub(r'\/', ":", uri.split("info/")[1])
    
# ############################# Driver ####################################

def main():

    runRecipes()
    
if __name__ == "__main__":
    main()

