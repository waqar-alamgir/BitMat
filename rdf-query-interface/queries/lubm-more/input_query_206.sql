PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ub: <http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#>
SELECT *
WHERE
{
    ?x ub:worksFor <http://www.Department9.University9999.edu> .
    ?x rdf:type <http://www.lehigh.edu/~zhp2/2004/0401/univ-bench.owl#FullProfessor>
}