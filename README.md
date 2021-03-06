# BitMat - In memory RDF Storage & Query Processing with Dual Simulation Pruning

For more information on BitMat please see: http://www.cse.iitk.ac.in/users/atrem<br>
For more details on Query Processing with Dual Simulation Pruning please see: https://www.slideshare.net/wajrcs/rdf-join-query-processing-with-dual-simulation-pruning

# Example Usage
Run the following commands to compile and execute:
<pre>
mkdir bin
mkdir output
make clean
make
./bin/bitmat -l y -Q y -f ./config/my.conf -q ./config/my.query -o ./output/result.txt
</pre>


# More Information

COMMON USAGE:
=============
$ ./bin/bitmat -l [y/n] -Q [y/n] -f configfile -q queryfile -o resultfile

Description:
  -l : Whether you want to load the data in BitMat format
  -Q : Whether you want to query the data. If this option is "n" then
       "-q" and "-o" options are ignored
  -f : Configfile. Should be formed as given in sample
  -q : Queryfile. Should be formed as given in sample
  -o : Path to the results file

---------------------------------------------------------------------

COMPILING:
==========
To compile the sources, follow two simple commands.

$ cd src
$ make

---------------------------------------------------------------------

DATA LOADING:
=============

Current BitMat code does not have way of parsing the RDF data. We use
an external script for that purpose.

The way of parsing the data and allocating unique IDs is same as
described in http://www.cs.rpi.edu/~atrem/papers/www10_medha.pdf in
Section 3.

After the ID allocation is done, we transform all the triples into
their ID representation. The original (S, P, O) triple is represented as
"SID:PID:OID".

This file is then sorted in 4 different ways as:

sort -u -n -t: -k2 -k1 -k3 encoded_triple_file > encoded_triple_file_spo
sort -u -n -t: -k2 -k3 -k1 encoded_triple_file | awk -F: '{print
	$3":"$2":"$1}' > encoded_triple_file_ops
sort -u -n -t: -k1 -k2 -k3 encoded_triple_file | awk -F: '{print
	$2":"$1":"$3}' > encoded_triple_file_pso
sort -u -n -t: -k3 -k2 -k1 encoded_triple_file | awk -F: '{print
	$2":"$3":"$1}' > encoded_triple_file_pos

This sorting gives us 4 different files where triples in their ID form
are sorted on 4 different orders viz. PSO, POS, SPO, and OPS.

We give paths to these 4 spo, ops, pso, and pos files in the configfile
as RAWDATAFILE_SPO, RAWDATAFILE_OPS etc (refer to the sample config
file in the "config" folder).

The BITMATDUMPFILE_SPO, BITMATDUMPFILE_OPS etc specify paths to the 4
types of BitMats created out of the given RDF data.

----------------------------------------------------------------------

CONFIG FILE:
============

Some important fields of cofig file:

1) TABLE_COL_BYTES: This field defines the number of bytes used to store
the offset of each BitMat inside the large file in which all BitMats are
stored one after another. This field is typically kept as "5" bytes to
allow for very large datasets. But for smaller datasets where the size
of the large metafile holding all the BitMats won't be greater than 4GB,
TABLE_COL_BYTES can be "4".

2) NUM_COMMON_SO: This field gives the number of common subject and
object URIs in the RDF dataset. 

3) ROW_SIZE_BYTES and GAP_SIZE_BYTES presently do not bear any
significance as those values are fixed in the code to be 4 bytes
which allows upto 4 billion distinct subject and object values.

4) COMPRESS_FOLDED_ARRAY: In our observation, typically if the dataset
has more than couple of hundred predicates (e.g. DBPedia which has
over 57000 predicates), setting COMPRESS_FOLDED_ARRAY to 1 achieves better
compression for indexes. Please use this configuration parameter for
datasets with large predicate values.

----------------------------------------------------------------------

QUERY PROCESSING:
=================

BitMat interface currently does not support a SPARQL parser. Each join
query is represented as follows:

1) Each join variable is assigned a negative integer ID.
2) Each fixed position in the triple pattern is replaced by the
respective string's ID (as was allocated during data loading step).
3) Each non-distinguished variable (non-join variable) is assigned
number "0".
4) Each triple pattern is then represented as, e.g., "-1:23:0" where
"-1" represents a join variable. "23" is the ID assigned to the
predicate in the original triple pattern and "0" is represents a
non-join variable in the query.
A sample query file is given in the "config" folder.
Anytihng beyond a line marked by "###" in the queryfile is ignored and
hence can be used for comments or to store the original text format
query.

----------------------------------------------------------------------

OUTPUT FORMAT:
==============

Since presently BitMat query processing interface does not support
SELECT clause of SPARQL query, it outputs all the variable bindings
(including join and non-join variables). The format in which it outputs
is: if the two triple patterns in the query are "-1:2:345" and "0:5:-1",
there is one variable binding value "678" for "-1" join variable, and
two variable bindings "4567", "8901" for the non-join variable
represented as "0", then the result looks like:

678:2:345:4567:5:678
678:2:345:8901:5:678

That is, the output result prints the entire triple values and not just
the variable bindings.


