import json
import logging
import os
import re
from hashlib import md5
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from azure.storage.blob import ContainerClient
from fuseki.utils import merge_json

logger = logging.getLogger(__name__)
GRAPHDB_URL = os.getenv("GRAPHDB_URL", "http://localhost:3030")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
KG_CONTAINER_NAME = "knowledge-graphs"  # TODO: os.getenv("AZURE_GRAPH_CONTAINER"), create env and put in helm values
LOCAL_STORAGE = os.getenv("LOCAL_STORAGE", True)


async def ping_fuseki(http_client: httpx.AsyncClient) -> bool:
    """Ping Fuseki to check if it is running

    Returns:
        bool: True if Fuseki can be pinged successfully, False otherwise
    """
    try:
        response = await http_client.get(urljoin(GRAPHDB_URL, "$/ping"))
    except (httpx.ConnectError, httpx.ConnectTimeout):
        return False
    try:
        response.raise_for_status()
        return True
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to ping Fuseki: {e}")
        return False


async def query_graph(q: str, dataset: str, http_client: httpx.AsyncClient) -> dict:
    """Query a graph in a Fuseki dataset

    Args:
        q (str): SPARQL query
        dataset (str): Name of the dataset

    Returns:
        dict: Response from the Fuseki server
    """
    response = await http_client.post(
        urljoin(GRAPHDB_URL, f"{dataset}/query"),
        data={"query": q},
    )

    response.raise_for_status()

    return response.json()


def clean_LiDO_ttl(source_file: Path):
    """Cleans syntax errors in LiDO TTL file to make it ingestible by Fuseki

    Args:
        source_file (Path): Path to the source TTL file
    """

    def fix_illegal_chars(line: str) -> str:
        return line.replace(r"<\>", "<")

    WHITESPACE_IN_IRI_PATTERN = re.compile(r"<https?:[^>]*\s+[^>]*>")

    def fix_whitespace_in_IRI(line: str) -> str:
        return re.sub(
            WHITESPACE_IN_IRI_PATTERN, lambda m: m.group(0).replace(" ", "-"), line
        )

    logger.info(f"Processing file {source_file}")
    with open(source_file, "r+b") as f:
        counter = 0
        while line := f.readline():
            counter += 1
            if counter % 1000000 == 0:
                logger.info(f"Processing line {counter}")

            fixed_line = fix_illegal_chars(
                fix_whitespace_in_IRI(line.decode("utf-8"))
            ).encode("utf-8")
            if fixed_line == line:
                continue

            logger.info(
                f"Fixing line {counter}: \"{line.decode('utf-8').strip()}\" -> \"{fixed_line.decode('utf-8').strip()}\""
            )

            if len(fixed_line) > len(line):
                raise ValueError(
                    f"Fixed line {counter} is longer than the original line"
                )

            position = f.tell()  # Save the current position in the file
            f.seek(f.tell() - len(line))  # Go back to the beginning of the line
            f.write(
                fixed_line.ljust(len(line))
            )  # Write the fixed line, padding with spaces if necessary
            f.seek(position)  # Go back to the end of the line

        logger.info(f"Finished processing file {source_file}")


async def ingest_ttl_file(
    http_client: httpx.AsyncClient, data_file: Path, dataset: str = "/ds"
):
    """Ingests a TTL file into a Fuseki dataset

    Args:
        data_file (Path): Path to the TTL file
        dataset (str): Name of the dataset
    """
    response = await http_client.post(
        urljoin(GRAPHDB_URL, f"{dataset}/data"),
        headers={"Content-Type": "text/turtle"},
        files={"data": data_file.open("rb")},
    )

    response.raise_for_status()
    logger.info(f"Successfully ingested data into dataset {dataset}")


async def ingest_ttl(
    http_client: httpx.AsyncClient, data: str, graph_name: str, dataset: str
):
    """Ingests TTL data into a Fuseki dataset"""
    try:
        response = await http_client.post(
            urljoin(
                GRAPHDB_URL, f"{dataset}/data?graph=http://example.org/{graph_name}"
            ),
            headers={"Content-Type": "text/turtle"},
            data=data,
        )
        response.raise_for_status()
        logger.info(f"Successfully ingested graph {graph_name} into dataset {dataset}")
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


async def ingest_graph_from_blob_storage(
    file_name: str, http_client: httpx.AsyncClient, dataset: str = "/ds"
):
    """Ingest TTL files from Azure Blob Storage into Fuseki"""
    try:
        ttl_string: str = ""

        if not LOCAL_STORAGE:
            container_client = ContainerClient.from_connection_string(
                AZURE_STORAGE_CONNECTION_STRING, KG_CONTAINER_NAME
            )
            blob_client = container_client.get_blob_client(file_name)
            if not blob_client.exists():
                logger.error(
                    f"Blob '{file_name}' does not exist. Listing available blobs:"
                )
                available_blobs = [blob.name for blob in container_client.list_blobs()]
                return f"Blob '{file_name}' does not exist. Available blobs: {available_blobs}"
            ttl_string = blob_client.download_blob().content_as_text()
        else:
            local_path = (
                Path(__file__).parent.parent.parent / "knowledge-graphs" / file_name
            )
            if not local_path.exists():
                return f"Local file '{local_path}' does not exist."
            with open(local_path, "r", encoding="utf-8") as file:
                ttl_string = file.read()
        graph_name = file_name.split(".")[0].lower()
        await ingest_ttl(
            http_client=http_client,
            data=ttl_string,
            graph_name=graph_name,
            dataset=dataset,
        )

        return f"Successfully ingested data from {'blob' if not LOCAL_STORAGE else 'local'} '{file_name}' into dataset {dataset} in Fuseki"
    except Exception as e:
        return f"Failed to ingest data from blob storage into Fuseki: {e}"
