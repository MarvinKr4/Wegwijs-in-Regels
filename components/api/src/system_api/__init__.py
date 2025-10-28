import logging
import os

from elastic import es, ingest
from elastic.ingest import ingest_from_blob_storage, ingest_from_local_storage
from elastic.model import create_indices
from fastapi import APIRouter, Depends
from fuseki.fuseki import ingest_graph_from_blob_storage, ping_fuseki
from http_client import get_http_client
from llm.llm import llm
from models import (
    ChatQuery,
    CSVFile,
    GraphFromBlobUpload,
    GraphLawQuery,
    GraphTaxonomyQuery,
)
from postgresql.data_processing import upload_csv_to_db
from postgresql.database import get_db
from rag.formulator import formulate_rag_answer
from rag.search import search
from services.kg_service import query_graph_lawuri, query_taxonomy
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/system", tags=["system"])

LOCAL_STORAGE = os.getenv("LOCAL_STORAGE", True)


@router.get("/health")
async def health(http_client=Depends(get_http_client)):
    return {
        "status_app": "running",
        "status_fuseki": "running" if await ping_fuseki(http_client) else "down",
        "status_elasticsearch": "running" if await es.ping() else "down",
    }


@router.get("/create-es-indices")
async def create_es_index():
    """
    Create Elasticsearch indices
    """
    await create_indices()
    return {"message": "Indices created"}


@router.get("/ingest-es-from-blob-storage")
async def ingest_es_blob_storage():
    """
    Trigger ES ingest from blob storage
    """
    if LOCAL_STORAGE:
        return await ingest_es_local_storage()

    n_docs = await ingest_from_blob_storage(
        container_name="legal-docs",
        doc_type="law",
    )
    return {"message": f"Ingested {n_docs} from blob storage"}


@router.get("/ingest-es-from-local-storage")
async def ingest_es_local_storage():
    """
    Trigger ES ingest from local storage
    """
    n_docs = await ingest_from_local_storage(
        doc_type="law",
    )
    return {"message": f"Ingested {n_docs} from local storage"}


@router.get("/ingest-case-law-from-blob-storage")
async def ingest_case_law_blob_storage():
    """
    Trigger case law ingest from blob storage
    """
    if LOCAL_STORAGE:
        return await ingest_case_law_local_storage()

    n_docs = await ingest_from_blob_storage(
        container_name="case-laws",
        doc_type="case-law",
    )
    return {"message": f"Ingested {n_docs} from blob storage"}


@router.get("/ingest-case-law-from-local-storage")
async def ingest_case_law_local_storage():
    """
    Trigger case law ingest from local storage
    """
    n_docs = await ingest_from_local_storage(
        doc_type="case-law",
    )
    return {"message": f"Ingested {n_docs} from local storage"}


@router.get("/ingest-werk-instructie-from-blob-storage")
async def ingest_werk_instructie_blob_storage():
    """
    Trigger werk instructie ingest from blob storage
    """
    if LOCAL_STORAGE:
        return await ingest_werk_instructie_local_storage()

    n_docs = await ingest_from_blob_storage(
        container_name="werk-instructie",
        doc_type="werk-instructie",
    )
    return {"message": f"Ingested {n_docs} from blob storage"}


@router.get("/ingest-werk-instructie-from-local-storage")
async def ingest_werk_instructie_local_storage():
    """
    Trigger werk instructie ingest from local storage
    """
    n_docs = await ingest_from_local_storage(
        doc_type="werk-instructie",
    )
    return {"message": f"Ingested {n_docs} from local storage"}


@router.post("/upload-graph")
async def upload_graph(
    graph: GraphFromBlobUpload, http_client=Depends(get_http_client)
):
    """
    Upload graph
    """
    logger.info(f"Retrieving graph {graph.blob_name} and uploading to Fuseki")

    result = await ingest_graph_from_blob_storage(graph.blob_name, http_client)
    return {"message": result}


@router.get("/graph-query-lawuri")
async def graph_query_graph_lawuri(
    query: GraphLawQuery, http_client=Depends(get_http_client)
):
    """Queries a graph in Fuseki based on a lawuri

    Args:
        query (GraphLawQuery): str: lawuri, str: graph name
        http_client (_type_, optional): _description_. Defaults to Depends(get_http_client).
    """
    logger.info(
        f"Querying graph http://example.org/{query.graph.lower()} for lawuri {query.lawuri}"
    )

    # Query the graph
    response = await query_graph_lawuri(query.lawuri, query.graph, http_client)
    return {"response": response}


@router.get("/query-taxonomy")
async def graph_query_taxonomy(
    query: GraphTaxonomyQuery,
    http_client=Depends(get_http_client),
):
    """
    .
    """
    logger.info(f"Querying graph {query.graph}.")

    # Query the graph
    response = await query_taxonomy(
        query.user_query,
        query.graph,
        http_client,
    )
    return {"response": response}


@router.post("/upload-csv")
def upload_csv(csv_file: CSVFile, db: Session = Depends(get_db)):
    """Upload csv file to database"""

    logger.info(f"Uploading CSV file {csv_file.file_name} to database")

    response = upload_csv_to_db(csv_file.file_name, db)

    logger.info(f"CSV file {csv_file.file_name} successfully uploaded to database")
    return {"message": response}


@router.post("/chat-rag")
async def chat_rag(chat_query: ChatQuery) -> str:
    """RAGchat

    Args:
        chat_query (ChatQuery): Chat query

    Returns:
        str: RAG response message
    """
    search_result = await search(chat_query.message)
    if len(search_result.documents) == 0:
        return "Ik heb geen relevante informatie kunnen vinden om deze vraag te beantwoorden."
    try:
        answer, source_index = await formulate_rag_answer(
            chat_query.message, search_result
        )
    except:
        return "Deze vraag kan ik helaas nog niet beantwoorden."
    if source_index is not None and source_index < len(search_result.documents):
        return (
            f"""{answer}\n\nVoornaamste bron: {search_result.laws[source_index]}, {search_result.titles[source_index]}\nLink: {search_result.urls[source_index]}""",
            search_result.urls,
        )
    return answer


@router.post("/chat-llm")
async def chat_llm(chat_query: ChatQuery):
    messages = [
        (
            "system",
            """Je bent een behulpzame assistent die vragen over de informatiewetten kan beantwoorden.""",
        ),
        ("human", chat_query.message),
    ]
    response = await llm.invoke(messages)
    logger.info(response)
    return {"message": response}
