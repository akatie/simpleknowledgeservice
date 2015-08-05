The location for (zipped) schemes. Only the latest versions of schemes will be in here. The zips contain definitions in both [JSON-LD](http://www.w3.org/TR/json-ld/) and [RDF Turtle](http://www.w3.org/TR/turtle/). The MongoDB and Fuseki importers expect the scheme definitions to be in this location and know how to read from these zips.

Current schemes (all about drugs) ...

Scheme | Version | Comment
--- | --- | --- 
ATC | 2015 | WHO Anatomical Therapeutic Chemical Classification System
FDAOB | 2015_06 | FDA Orange Book
MTHSPL | 2015_07_24 | MTHSPL has the latest NDC data
NCIT | 15.06e | Subset referenced from MTHSPL
NDFRT | 2015_07_06 | VA National Drug File Reference Terminology (FDA classing, Disease effects and more)
RXNORM | 15AA_150803F | RXNORM with matches to other schemes
UNII | 2July2015 | Latest ingredient/chemical compounds from the FDA. Used in MTHSPL. Linked to drug classes by NDFRT

Example of RxNORM's definition of _Nexium 20mg Extended Release Oral Tablet_ ...

```json
        {
            "type": "skos:Concept",
            "id": "rxnorm:606728",
            "prefLabel": "Esomeprazole 20 MG Delayed Release Oral Capsule [Nexium]",
            "altLabel": [
                "Nexium 20 MG Delayed Release Oral Capsule",
                "Nexium 24 HR 20 MG Delayed release Oral Capsule",
                "Nexium 20 MG (as esomeprazole magnesium 22.3 MG) Delayed Release Oral Capsule"
            ],
            "code": "606728",
            "inScheme": {
                "id": "rxnorm:scheme"
            },
            "broaderTop": {
                "id": "rxnorm:SBD"
            },
            "umlsCUI": "C1637815",
                        
            "rxnormo:tradename_of": {
                "id": "rxnorm:606726"
            },
            "rxnormo:has_component": {
                "id": "rxnorm:574982"
            },
            "rxnormo:has_ingredient_and_form": {
                "id": "rxnorm:606727"
            },
            "rxnormo:prescribable": true,
            "rxnormo:human_drug": true
        },
```

