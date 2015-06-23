Use MongoDB for a simple medical knowledge service

1. Load a scheme's definitions into a MongoDB collection
2. Report on the basic shape of the scheme
3. Recipes for common tasks in various domains - drugs, labs, disorders - that go across schemes. The simplest of these are matches where, for example, given an NDC drug code, you want to find the RxNORM normalizing code.
 
Note: we're starting with drug schemes (RxNORM, MTHSPL (NDC), FDA classes ...) and will move on from there to disorders (SNOMED, ICD9, ...)
