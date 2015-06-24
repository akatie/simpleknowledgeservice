Use MongoDB for a Simple (Medical) Knowledge Service

The MongoDB package contains:

1. loadSchemes.py: loads available schemes into MongoDB, with one collection per scheme
2. reportSchemes.py: basic report on the loaded schemes
3. *Recipes.py: "recipes" for common knowledge tasks in various domains. The first set is for drug schemes.
 
As the _.py_ suggests, the code is in Python which is built into Linux and OS X and is easy to install on Windows. From the command line, just
call 

    python loadSchemes.py

or 

    ./loadSchemes.py

Typical output from the routines are in README_OUTPUT_*

Note: we're starting with drug schemes (RxNORM, MTHSPL (NDC), FDA classes ...) and will move on from there to disorders (SNOMED, ICD9, ...) and then labs (LOINC).
