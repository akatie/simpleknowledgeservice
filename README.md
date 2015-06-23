# Medical Knowledge Organization System (MKOS)
all you need for a simple medical knowledge service. Not a simplistic knowledge service or a service for simplistic knowledge but a straightforward, consistent service for medical knowledge.

Fully exploiting SKOS - the standard [Simple Knowledge Organization System](http://www.w3.org/2004/02/skos/) - for Medical Knowledge Schemes, the RxNORMs, SNOMEDs, LOINCs and ICDs that frame medical expression.

Add in another flavor of today, JSON-LD, _the ... of JSON_, and you have what you need to make a system for representing, comparing, measuring and reasoning upon medical knowledge irrespective of its original data format.

>> In every field of inquiry, it is true that all things should be made as simple as possible – but no simpler.

In-between excel spreadsheets and crude lookup tables and the lofty towers of ontologies and orders of logic lies a middle ground where knowledge can be
represented consistently, compared, translated, measured and reasoned upon with a minimum of frills and theory.

Property | Data
--- | ---
Format | JSON-LD
Model | SKOS
Stores | Graph or MongoDB
Coverage | freely available, government and 3rd party medical knowledge schemes

* up-to-date. We will publish updates to schemes once they are available. This is NOT an academic exercise.

We want a service that

  * accurately captures the complete contents of existing knowledge schemes. We don't want to start guessing which subset is appropriate for every future purpose. We want to know about all that's available, quantify it and move on from there.
  * translates ("matches") between schemes and within schemes, rolling up what consistutes classes of concepts
  * reduces the redundancy and overlaps between schemes including prioritizing "anchor" schemes

and can be implemented in everyday media. Today a knowledge representation often means a graph - think Google's Knowledge Graph or Microsoft's Satori - but while we want to show a graph based service, we also want to address knowledge in the popular document or file based stores like MongoDB where much application development takes place today. 

but we are not (yet) concerned with adding concepts to existing schemes or coining new schemes. We want to properly represent what exists now and use it better.

We don't want to make up our own data format for scheme definition - we'll use JSON-LD because that's what's popular and it fits - and we don't want to make our own terminology for defining these terminologies - we'll use SKOS.

And perhaps most importantly, we don't want to be academic, always behind in our data. From the start, we'll publish datasets on time - as raw data becomes available, we'll update the schemes on this site.
