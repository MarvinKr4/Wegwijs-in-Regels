import json
import logging
import os
import re
from hashlib import md5
from typing import Any
from urllib.parse import quote, urljoin

import httpx
from fuseki.utils import merge_json
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

logger = logging.getLogger(__name__)


GRAPHDB_URL = os.getenv("GRAPHDB_URL", "http://localhost:3030")

tokenizer = RegexpTokenizer(r"\w+")


async def query_graph_lawuri(
    law_uri: str, graph_name: str, http_client: httpx.AsyncClient, dataset: str = "/ds"
) -> dict:
    """Query all related triples for a given jas:orgArtikel with the
        specified law URI in the given graph.

    Args:
        law_uri (str): The law URI to query for.
        graph_name (str): The name of the graph to query.
        http_client (httpx.AsyncClient): The HTTP client to use for the query.

    Returns:
        dict: The response from the Fuseki server.
    """
    try:
        if graph_name.lower() == "jas":
            query = f"""
            PREFIX jas: <http://www.nl/>
            PREFIX lido: <http://linkeddata.overheid.nl/terms/bwb/id#>

            SELECT ?subject ?predicate ?object
            FROM  <http://example.org/jas>
            WHERE {{
            ?subject jas:orgArtikel lido:{law_uri} .
            ?subject ?predicate ?object .
            }}
            """
        elif graph_name.lower() == "lido":
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX overheidrl: <http://linkeddata.overheid.nl/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            SELECT ?predicate ?object
            FROM <http://example.org/lido>
            WHERE {{
                <{law_uri}> ?predicate ?object .
            }}
            """

        response = await http_client.post(
            urljoin(GRAPHDB_URL, f"{dataset}/query"),
            data={"query": query},
        )

        response.raise_for_status()

        if response.json()["results"]["bindings"]:
            return response.json()
        else:
            return {"message": "No results found for the given law URI."}
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to query Fuseki {graph_name} graph:{e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


def extract_bwbr_and_article(url: str):
    # Extract BWBR ID using regex
    bwbr_match = re.search(r"BWBR\d{6,7}", url)
    bwbr_id = bwbr_match.group(0) if bwbr_match else None

    # Extract article number using regex
    artikel_match = re.search(r"artikel=(\d+\.\d+|\d+)", url)
    artikel_nummer = artikel_match.group(1) if artikel_match else None

    return bwbr_id, artikel_nummer


async def get_article_uri(
    bwbr_id: str,
    article_number: str,
    http_client: httpx.AsyncClient,
    dataset: str = "/ds",
) -> str:
    """
    Query the Fuseki database to retrieve the URI of an article based on
    BWBR ID and article number.

    :param bwbr_id: The BWBR number (e.g., "BWBR0011468").
    :param article_number: The article number as a string (e.g., "19").
    :param http_client: The HTTP client to use for the query.
    :param dataset: The dataset to query in Fuseki.
    :return: The URI of the matching article or None if not found.
    """
    try:
        sparql_query = f"""
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT ?articleUri
        FROM <http://example.org/lido>
        WHERE {{
            ?articleUri skos:prefLabel ?label .
            FILTER(CONTAINS(STR(?articleUri), "{bwbr_id}")) .
            FILTER(CONTAINS(LCASE(STR(?label)), "artikel {article_number}")) .
        }}
        """

        response = await http_client.post(
            urljoin(GRAPHDB_URL, f"{dataset}/query"),
            data={"query": sparql_query},
        )

        response.raise_for_status()

        if response.json()["results"]["bindings"]:
            return response.json()["results"]["bindings"][0]["articleUri"]["value"]
        else:
            return None

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to query Fuseki to get article uri: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


def encode_bwb_uri(uri: str) -> str:
    # Extract the part starting from "BWBR"
    bwbr_part = uri.split("bwb/id/")[-1]
    # Encode slashes
    return quote(bwbr_part, safe="")


async def query_taxonomy(
    user_query: str,
    graph_name: str,
    http_client: httpx.AsyncClient,
    dataset: str = "/ds",
) -> Any:
    logger.info(user_query)
    logger.info(graph_name)
    logger.info(http_client)

    query_responses = []
    md5_set = set()

    # To avoid unnecessary searches, tokenize the user query and remove any stopwords.
    tokens = tokenizer.tokenize(user_query.lower())
    dutch_stopwords = stopwords.words("dutch")
    seen_words = set()

    for word in [word for word in tokens if word not in dutch_stopwords]:
        if word not in seen_words:
            logger.info(f'Looking up "{word}"')
            seen_words.add(word)
        else:
            continue

        taxonomy_query = f"""
        PREFIX beg-sbb: <http://begrippen.nlbegrip.nl/sbb/id/concept/>
        PREFIX wir: <http://www.koopoverheid.nl/WegwijsinRegels#>

        SELECT ?concept ?label ?definition ?source ?naderToegelicht ?scoopNote ?wetcontext ?NarrowerGeneric ?AltLabel ?BroaderGeneric ?opGrondVan
        FROM  <http://example.org/{graph_name.lower()}>
        WHERE {{
            ?concept beg-sbb:Label ?label .

            OPTIONAL {{ ?concept beg-sbb:Source ?conceptSource . }}                   # Direct source
            OPTIONAL {{ ?concept wir:naderToegelicht ?conceptNaderToegelicht . }}     # Direct naderToegelicht
            OPTIONAL {{ ?concept beg-sbb:Definition ?conceptDefinition . }}           # Direct definition
            OPTIONAL {{ ?concept beg-sbb:ScopeNote ?conceptScopeNote . }}             # Direct scopeNote
            OPTIONAL {{ ?concept wir:wetcontext ?conceptWetcontext . }}               # Direct wetcontext
            OPTIONAL {{ ?concept beg-sbb:NarrowerGeneric ?conceptNarrowerGeneric . }}     # NarrowerGeneric
            OPTIONAL {{ ?concept beg-sbb:AltLabel ?conceptAltLabel . }}                   # AltLabel
            OPTIONAL {{ ?concept beg-sbb:BroaderGeneric ?conceptBroaderGeneric . }}       # BroaderGeneric
            OPTIONAL {{ ?concept wir:opGrondVan ?conceptOpGrondVan . }}               # opGrondVan

            # Handle blank concepts containing wetcontext and Source
            OPTIONAL {{
                ?concept wir:context ?context .
                OPTIONAL {{ ?context beg-sbb:Definition ?contextDefinition . }}
                OPTIONAL {{ ?context beg-sbb:Source ?contextSource . }}
                OPTIONAL {{ ?context wir:naderToegelicht ?contextNaderToegelicht . }}
                OPTIONAL {{ ?context beg-sbb:ScopeNote ?contextScopeNote . }}
                OPTIONAL {{ ?context wir:wetcontext ?contextWetcontext . }}

                OPTIONAL {{ ?context beg-sbb:NarrowerGeneric ?contextNarrowerGeneric . }}
                OPTIONAL {{ ?context beg-sbb:AltLabel ?contextAltLabel . }}
                OPTIONAL {{ ?context beg-sbb:BroaderGeneric ?contextBroaderGeneric . }}
                OPTIONAL {{ ?context wir:opGrondVan ?contextopGrondVan . }}
            }}

            # Ensure we retrieve both direct and blank concept references
            BIND(COALESCE(?conceptNaderToegelicht, ?contextNaderToegelicht) AS ?naderToegelicht)
            BIND(COALESCE(?conceptSource, ?contextSource) AS ?source)
            BIND(COALESCE(?conceptDefinition, ?contextDefinition) AS ?definition)
            BIND(COALESCE(?conceptScopeNote, ?contextScopeNote) AS ?scoopNote)
            BIND(COALESCE(?conceptWetcontext, ?contextWetcontext) AS ?wetcontext)
            BIND(COALESCE(?conceptNarrowerGeneric, ?contextNarrowerGeneric) AS ?NarrowerGeneric)
            BIND(COALESCE(?conceptAltLabel, ?contextAltLabel) AS ?AltLabel)
            BIND(COALESCE(?conceptBroaderGeneric, ?contextBroaderGeneric) AS ?BroaderGeneric)
            BIND(COALESCE(?conceptOpGrondVan, ?contextopGrondVan) AS ?opGrondVan)


            FILTER(CONTAINS(LCASE(STR(?label)), \"{word}\"))
        }}
        """

        try:
            response: httpx.Response = await http_client.post(
                urljoin(GRAPHDB_URL, f"{dataset}/query"),
                data={"query": taxonomy_query},
            )

            logger.info(response.json()["results"]["bindings"])
            response.raise_for_status()
            sub_results = []

            result = response.json()["results"]["bindings"]

            # To avoid duplicate results, loop through the sub results and check the md5 digest value against a set of previously seen md5 values.
            for sub_result in result:

                md5_result = md5(json.dumps(sub_result).encode()).digest()

                if md5_result in md5_set:
                    logger.info(
                        f"""
md5 value, {md5_result}, for {sub_result["label"]["value"]=} for {word=} already in set. Continuing...
                        """
                    )
                    continue

                md5_set.add(md5_result)
                logger.info(md5_result)
                sub_results.append(sub_result)

            # Finally, add the sub results to the main list of results.
            logger.info(f"Appending {sub_results=} to query_responses")
            query_responses.append(sub_results)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    merged_json = merge_json(query_responses)
    return merged_json
