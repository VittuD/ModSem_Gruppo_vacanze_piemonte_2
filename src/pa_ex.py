import pysparql_anything as sa

engine = sa.SparqlAnything()

engine.run(query='./queries/author.sparql',output='./output/ex_author.ttl',format='ttl')