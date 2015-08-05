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
import urllib, urllib2
from datetime import datetime
    
"""
All schemes have one ConceptScheme description. It contains a
mixture of general and per version meta data about a scheme. This
set of routines will print out these details about the schemes
in a Simple Knowledge Service's Triple Store as well as walk down to 
the key organizing concepts ("Broader Tops") of the scheme.

Note: the MongoDB SKS has an equivalent of this set of routines
"""

FUSEKI_QUERY_URI = "http://localhost:3030/sks/query"

def reportSchemes():

    print
    print "######################### Report on Schemes of Fuseki at", FUSEKI_QUERY_URI, "#########################"

    print
    print "Query graphs with schemes ..."
    print    
    QUERY_GRAPHS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?g ?s WHERE {GRAPH ?g {?s a skos:ConceptScheme}} ORDER BY ?g
    """
    query = QUERY_GRAPHS
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    graphsNSchemes = [(binding["g"]["value"], sciURIToNSForm(binding["s"]["value"])) for binding in json.loads(urllib2.urlopen(request).read())["results"]["bindings"]]
    print "Have", len(graphsNSchemes), "schemes, each with their own graph:"
    for i, (graph, scheme) in enumerate(graphsNSchemes, 1):
        print "\t", i, scheme, graph
    print 
        
    print "######################### Scheme basics, scheme by scheme ###################"
    for graph, scheme in graphsNSchemes:
        reportScheme(graph, scheme)
    print
    print
        
    print "######################### Graph basics, graph by graph ###################"
    print "... slower than quick scheme queries as doing a lot of explicit graph walks"
    for graph, scheme in graphsNSchemes:
        reportGraph(graph)
    print
    
def reportScheme(graph, scheme):
    """
    Only interested in the ConceptScheme resource, the one with id
            <schemeMN>:scheme
    It contains a mixture of meta data about a particular version of a scheme.
    
    As there is one scheme per graph, there will be one ConceptScheme resource
    per graph.
    """
    
    print
    print "=============== About scheme", scheme, "================"
    print

    QUERY_SCHEME_DESCRIPTION = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?p ?o
    FROM <%s>
    WHERE {
        ?s a skos:ConceptScheme ;
           ?p ?o
    }
    """
    query = QUERY_SCHEME_DESCRIPTION % graph
    print "Query 'ConceptScheme' details ..." 
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    schemeDescription = {}
    for binding in reply["results"]["bindings"]:
        schemeDescription[sciURIToNSForm(binding["p"]["value"])] = binding["o"]["value"] if binding["o"]["type"] == "literal" else sciURIToNSForm(binding["o"]["value"])

    print "Reply ..."
    # Leaving out "umlsCUI", "referencedSchemes", "hasTopConcept", "sourceFormat"
    print    
    print "\t-------------- details --------------"  
    print "\tLabel:", schemeDescription["skos:prefLabel"] 
    if "skos:definition" in schemeDescription:
        print "\tDefinition:"
        print "\t\t", schemeDescription["skos:definition"]
    print "\tVersion:", schemeDescription["owl:versionInfo"]
    print "\tLast update:", schemeDescription["cgkos:lastUpdate"]
    print "\tCopyright:"
    print "\t\t", schemeDescription["cgkos:copyright"]

    """
    Note that the statistics could be explicitly queried but that takes much longer as
    you can see in "reportGraph".
    ex/ # deprecated:
            SELECT (COUNT(*) AS ?noDeprecated)
            WHERE {
                ?c a skos:Concept .
                EXISTS {?c owl:deprecated []}
            } 
    """    
    print
    print "\t-------------- statistics --------------"
    # Statistics are from the VoID schema (http://www.w3.org/TR/void/) and Caregraf 
    # additions. Some include ...
    STAT_PREDS = [("void:distinctSubjects", "Subjects"), ("void:triples", "Total Assertions"), ("cgkos:literalTriples", "Property Assertions"), ("cgkos:edgeTriples", "Graph Assertions"), ("cgkos:matched", "Matches"), ("cgkos:broaderTops", "Top Concepts")]
    for predInfo in STAT_PREDS:
        if predInfo[0] not in schemeDescription:
            continue
        print "\t" + predInfo[1] + ":", schemeDescription[predInfo[0]]
    print
    print
   
    """
    Unless a scheme is flat (it has no hierarchy), it will have two or more 'top concepts'. These are the main organizing concepts of a scheme ("Drug", "Dose Form" ... for RxNORM) or ("Clinical Finding", "Substance" for SNOMED).
    """
    # Not flat if hasTopConcepts
    ASK_IF_TOP_CONCEPTS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    ASK
    FROM <%s>
    WHERE {
        ?s a skos:ConceptScheme ;
           skos:hasTopConcept ?tc
    }
    """
    print "ASK 'Scheme has topConcepts' - is it flat or structured? ..."
    query = ASK_IF_TOP_CONCEPTS % graph
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    if reply["boolean"] == False:
        print "... no top concepts so Scheme is Flat. Nothing to report on its breakdown."
        print
        return
        
    """
    Note: we could just query topConcepts from "hasTopConcept" in Scheme resource
    and each of those concepts come with an annotation of how many subordinates they
    have.
    
    TODO: combine with description below
    """
    QUERY_TOP_CONCEPTS_AND_COUNTS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX cgkos: <http://schemes.caregraf.info/ontology#>
    SELECT ?topCLabel (COUNT(DISTINCT ?c) AS ?numberSubordinates)
    FROM <%s>
    WHERE {
        ?c cgkos:broaderTop ?topC .
        ?topC skos:prefLabel ?topCLabel
    }
    GROUP BY ?topCLabel
    ORDER BY DESC(?numberSubordinates)
    """
    print "Query 'Top Concepts' and Counts ..."
    query = QUERY_TOP_CONCEPTS_AND_COUNTS % graph
    print query
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())

    print "Reply ..."
    print
    # TODO: check if has topConcept(s)
    mostPopularTopConceptLabel = ""
    if not sum(1 for binding in reply["results"]["bindings"] if "topCLabel" in binding):
        print "\t------------- Flat Scheme - no top concepts ---------"
    else:
        print "\t-------------- Top Concepts --------------"
        print "\t... the organizing concepts"
        print    
        for i, binding in enumerate(reply["results"]["bindings"], 1):
            if i == 1: # most popular BT is the first as sorting
                mostPopularTopConceptLabel = binding["topCLabel"]["value"]
            print "\t", i, binding["topCLabel"]["value"]
            print "\t\tChildren", binding["numberSubordinates"]["value"]
            
    if not mostPopularTopConceptLabel:
        raise Exception("Assumed all structured - not flat - schemes have a most popular TC!")
          
    """
    Let's display a child of the most popular broader top, one that hasn't been retired
    (deprecated). 
    
    All inactive/retired concepts with have the value 'true' for 'deprecated'. 
    Active concepts won't have a 'deprecated' field.
    
    If a scheme supports matches to other schemes then make sure the example is matched.
    
    First get one. Note: doing explicitly as DESCRIBE LIMIT 1 won't work if embedded
    blank nodes as blanks appear explicitly. 
    """    
    print
    print "\t-------------- Get an (Active) concept of the most popular type ----"
    QUERY_ONE_MOST_POPULAR = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX cgkos: <http://schemes.caregraf.info/ontology#>
    SELECT ?s
    FROM <%s>
    WHERE {
        ?tcId skos:prefLabel "%s" .
        ?s cgkos:broaderTop ?tcId .
        FILTER NOT EXISTS {?s owl:deprecated []}
    }
    LIMIT 1
    """
    print "Query ..."
    query = QUERY_ONE_MOST_POPULAR % (graph, mostPopularTopConceptLabel)
    print query
    print
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    exMostPopularId = reply["results"]["bindings"][0]["s"]["value"]
    
    print 
    print "\t-------------- Example (Active) Concept", exMostPopularId, "--------------"
    QUERY_SAMPLE_CONCEPT = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX cgkos: <http://schemes.caregraf.info/ontology#>
    SELECT ?p ?o
    FROM <%s>
    WHERE {
        <%s> ?p ?o
    }
    """
    print "Query ..."
    schemeNS = scheme.split(":")[0] # ie/ atc:scheme -> "atc"
    query = QUERY_SAMPLE_CONCEPT % (graph, exMostPopularId)
    print query
    print
    # Note: for DESCRIBE in Jena, "json" now means "json-ld"
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "json"})
    request = urllib2.Request(queryurl)
    reply = json.loads(urllib2.urlopen(request).read())
    for binding in reply["results"]["bindings"]:
        pred = re.search(r'([^\#\:\/]+)$', binding["p"]["value"]).group(1)
        if binding["o"]["type"] == "bnode":
            print "\t", pred + ":", "** Blank Node Value - must query again for it"
            continue
        print "\t", pred + ":", binding["o"]["value"] if binding["o"]["type"] != "uri" else sciURIToNSForm(binding["o"]["value"])
    print
    
def reportGraph(graph):
    """
    Report on scheme graph as a graph ie/ totals of resources, types of
    resources ie/ applies to any graph.
    
    Brute force queries that can take a while
    """
    
    print
    print "=============== About graph", "<" + graph + ">", "as a graph================"
    print "... for larger graphs, these take a while as to count every applicable entity (resource or assertion) must be walked"
    print
    
    # This is <=> number of documents in MongoDB
    print "Query number of typed resources ..."
    QUERY_COUNT_TYPED_RESOURCES = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT (COUNT(*) AS ?noTypedResources)
    FROM <%s>
    WHERE {
        ?r a []
    }
    """
    query = QUERY_COUNT_TYPED_RESOURCES % graph
    print query
    # Note: using 'text' output as this is a report
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "text"})
    request = urllib2.Request(queryurl)
    print urllib2.urlopen(request).read()
    print
    
    print "Query types of resources ..."
    print "... always the same two for these Knowledge Graphs, skos:Concept and skos:ConceptScheme"
    QUERY_RESOURCE_TYPES = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?type
    FROM <%s>
    WHERE {
        ?r a ?type
    }
    """
    query = QUERY_RESOURCE_TYPES % graph
    print query
    # Note: using 'text' output as this is a report
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "text"})
    request = urllib2.Request(queryurl)
    print urllib2.urlopen(request).read()
    print
    
    print "Query number of graph/edge (object is resource) assertions ..."
    print "... takes a while if graph is large"
    QUERY_COUNT_GRAPH_ASSERTIONS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT (COUNT(*) AS ?noGraphAssertions)
    FROM <%s>
    WHERE {
        ?r ?p ?o . FILTER isIRI(?o)
    }
    """
    query = QUERY_COUNT_GRAPH_ASSERTIONS % graph
    print query
    # Note: using 'text' output as this is a report
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "text"})
    request = urllib2.Request(queryurl)
    print urllib2.urlopen(request).read()
    print
    
    print "Query number of graph (object is string/int/date) assertions ..."
    print "... takes a while if graph is large"
    QUERY_COUNT_LITERAL_ASSERTIONS = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT (COUNT(*) AS ?noLiteralAssertions)
    FROM <%s>
    WHERE {
        ?r ?p ?o . FILTER isLiteral(?o)
    }
    """
    query = QUERY_COUNT_LITERAL_ASSERTIONS % graph
    print query
    # Note: using 'text' output as this is a report
    queryurl = FUSEKI_QUERY_URI + "?" + urllib.urlencode({"query": query, "output": "text"})
    request = urllib2.Request(queryurl)
    print urllib2.urlopen(request).read()
    print
            
def sciURIToNSForm(uri):
    """
    Pretty-ups most concept URIs by replacing full expansion with namespaced form.
    
    Ex/ http://schemes.caregraf.info/rxnorm/scheme -> rxnorm:scheme 
    """
    if not re.match(r'http', uri):
        return uri
    SMAP = {"http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf", "http://www.w3.org/2004/02/skos/core#": "skos", "http://rdfs.org/ns/void#": "void", "http://schemes.caregraf.info/ontology#": "cgkos", "http://www.w3.org/2002/07/owl#": "owl"}
    for suri in SMAP:
        if re.match(suri, uri):
            return SMAP[suri] + ":" + re.sub(suri, "", uri)
    if not re.search(r'schemes\.caregraf\.info', uri):
        return uri
    return re.sub(r'\/', ":", uri.split("info/")[1])
        
# ############################# Driver ####################################

def main():

    reportSchemes()
    
if __name__ == "__main__":
    main()
