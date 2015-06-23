# Simple Schemes Service (TripleS)
all you need for a simple medical knowledge service. Not a simplistic knowledge service or a service for simplistic knowledge but a straightforward, consistent service for medical knowledge.

>> In every field of inquiry, it is true that all things should be made as simple as possible – but no simpler.

In-between excel spreadsheets and crude lookup tables and the lofty towers of ontologies and orders of logic lies a middle ground where knowledge can be
represented consistently, compared, translated, measured and reasoned upon with a minimum of frills and theory.

Not going beyond Knowledge Schemes to other forms of meta data, to data models or elaborate document templates.

Take the scheme graphs produced by kGrafer and produce a knowledge service in two flavors, one based on a JSON-document store MongoDB and the other a RDF-backed graph store.

Why these examples? Why not a single server in one technology? Well, the goal here is a service for use inside other services. In practice, you don't call for knowledge over a network, no matter how fast. You embed knowledge within your service.

## Priorities

to

  * accurately capture the complete contents of existing knowledge schemes. We don't want to start guessing which subset is appropriate for every future purpose
  * translate ("match") between knowledge schemes
  * reduce the redundancy and overlaps between schemes including prioritizing "anchor" schemes
  * frame knowledge to suit the medium: document/file store like MongoDB may have different needs from a Graph store and we'll explore knowledge representation in both media

not (yet) concerned with adding concepts to existing schemes or introducing new schemes. The focus is on what already exists and making it easy to exploit.


