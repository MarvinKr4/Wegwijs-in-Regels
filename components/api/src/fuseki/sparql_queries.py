TEST_QUERY = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?node
    WHERE {
    ?node ?p <http://linkeddata.overheid.nl/terms/bwb/id/BWBR0045754/16045964/2024-08-01/2024-08-01> .
    }
"""


TEST_QUERY_2 = """PREFIX jas: <http://www.nl/>
PREFIX lido: <http://linkeddata.overheid.nl/terms/bwb/id#>

SELECT ?subject ?orgArtikel WHERE {
  GRAPH <http://example.org/jas> {
    ?subject jas:orgArtikel ?orgArtikel .
    FILTER(CONTAINS(STR(?orgArtikel), "BWBR0007376"))
  }
}
"""

QUERY_LAWURI = """
PREFIX jas: <http://www.nl/>
PREFIX lido: <http://linkeddata.overheid.nl/terms/bwb/id#>

SELECT ?subject ?predicate ?object
WHERE {
    GRAPH <http://example.org/jas>  {
  ?subject jas:orgArtikel lido:BWBR0045754%2F16045034%2F2022-05-01%2F2022-05-01 .
  ?subject ?predicate ?object .
  }
}
"""

ALTERNATIVE_LAWURI_QUERY = """
    PREFIX jas: <http://www.nl/>
    PREFIX lido: <http://linkeddata.overheid.nl/terms/bwb/id#>

    SELECT ?subject ?predicate ?object
    FROM  <http://example.org/jas>
    WHERE {
    ?subject jas:orgArtikel lido:BWBR0045754%2F16045034%2F2022-05-01%2F2022-05-01 .
    ?subject ?predicate ?object .
    }
    """
