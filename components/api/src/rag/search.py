import logging

from elastic.model import (
    CaseLawChunk,
    CaseLawDocument,
    Chunk,
    LegalDocument,
    WerkInstructieChunk,
    WerkInstructieDocument,
)
from llm.llm import get_embedding
from models import (
    VectorSearchCaseLawResult,
    VectorSearchResult,
    VectorSearchWerkInstructieResult,
)

logger = logging.getLogger(__name__)
SIMILARITY_THRESHOLD = 0.5


async def search(query: str) -> VectorSearchResult:
    logger.info(f"Searching for: {query}")

    query_embedding = await get_embedding(query)

    relevant_chunks = [
        chunk
        async for chunk in Chunk.search()
        .knn(
            field="embedding",
            k=50,
            num_candidates=100,
            query_vector=query_embedding,
            similarity=SIMILARITY_THRESHOLD,
        )
        .iterate()
    ]
    logger.info(f"Found {len(relevant_chunks)} relevant chunks in function: {__name__}")

    relevant_doc_ids = list({chunk.document_id for chunk in relevant_chunks})
    if not relevant_doc_ids:
        logger.info("No relevant documents found")
        return VectorSearchResult(documents=[], chunks=[], titles=[], laws=[], urls=[])

    relevant_docs = await LegalDocument.mget(relevant_doc_ids)

    logger.info(f"Found {len(relevant_docs)} relevant documents")
    for doc in relevant_docs:
        logger.info(
            f'Found document with the title: "{doc.title}", in the "{doc.law_name}" law.\nURL: {doc.url}'
        )

    return VectorSearchResult(
        documents=[doc.body for doc in relevant_docs],
        chunks=[
            [
                str(chunk.chunk_text)
                for chunk in relevant_chunks
                if chunk.document_id == doc_id
            ]
            for doc_id in relevant_doc_ids
        ],
        laws=[doc.law_name for doc in relevant_docs],
        titles=[doc.title for doc in relevant_docs],
        urls=[doc.url for doc in relevant_docs],
    )


async def search_case_laws(query: str) -> VectorSearchCaseLawResult:
    logger.info(f"Searching for: {query}")

    query_embedding = await get_embedding(query)

    relevant_chunks = [
        chunk
        async for chunk in CaseLawChunk.search()
        .knn(
            field="embedding",
            k=50,
            num_candidates=100,
            query_vector=query_embedding,
            similarity=SIMILARITY_THRESHOLD,
        )
        .iterate()
    ]
    logger.info(f"Found {len(relevant_chunks)} relevant chunks in function: {__name__}")

    relevant_doc_ids = list({chunk.document_id for chunk in relevant_chunks})
    if not relevant_doc_ids:
        logger.info("No relevant documents found")
        return VectorSearchCaseLawResult(
            documents=[],
            chunks=[],
            titles=[],
            inhoudsindicaties=[],
            date_uitspraken=[],
            case_numbers=[],
            urls=[],
        )

    relevant_docs = await CaseLawDocument.mget(relevant_doc_ids)

    logger.info(f"Found {len(relevant_docs)} relevant documents")
    for doc in relevant_docs:
        logger.info(
            f'Found document with the title: "{doc.title}", in the case law with case number: "{doc.zaaknummer}".\nURL: {doc.url}'
        )

    return VectorSearchCaseLawResult(
        documents=[doc.uitspraak for doc in relevant_docs],
        chunks=[
            [
                str(chunk.chunk_text)
                for chunk in relevant_chunks
                if chunk.document_id == doc_id
            ]
            for doc_id in relevant_doc_ids
        ],
        case_numbers=[doc.zaaknummer for doc in relevant_docs],
        titles=[doc.title for doc in relevant_docs],
        inhoudsindicaties=[doc.inhoudsindicatie for doc in relevant_docs],
        date_uitspraken=[doc.datum_uitspraak for doc in relevant_docs],
        urls=[doc.url for doc in relevant_docs],
    )


async def search_werk_instructies(query: str) -> VectorSearchWerkInstructieResult:
    logger.info(f"Searching for: {query}")

    query_embedding = await get_embedding(query)

    relevant_chunks = [
        chunk
        async for chunk in WerkInstructieChunk.search()
        .knn(
            field="embedding",
            k=50,
            num_candidates=100,
            query_vector=query_embedding,
            similarity=SIMILARITY_THRESHOLD,
        )
        .iterate()
    ]
    logger.info(f"Found {len(relevant_chunks)} relevant chunks in function: {__name__}")

    relevant_doc_ids = list({chunk.document_id for chunk in relevant_chunks})
    if not relevant_doc_ids:
        logger.info("No relevant documents found")
        return VectorSearchWerkInstructieResult(
            documents=[], chunks=[], titles=[], urls=[]
        )

    relevant_docs = await WerkInstructieDocument.mget(relevant_doc_ids)

    logger.info(f"Found {len(relevant_docs)} relevant documents")
    for doc in relevant_docs:
        logger.info(
            f'Found document with the title: "{doc.title}", in the werk instructie woo.\nURL: {doc.url}'
        )

    return VectorSearchWerkInstructieResult(
        documents=[doc.body for doc in relevant_docs],
        chunks=[
            [
                str(chunk.chunk_text)
                for chunk in relevant_chunks
                if chunk.document_id == doc_id
            ]
            for doc_id in relevant_doc_ids
        ],
        titles=[doc.title for doc in relevant_docs],
        urls=[doc.url for doc in relevant_docs],
    )
