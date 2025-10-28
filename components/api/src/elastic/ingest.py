import json
import logging
import os
import uuid
from pathlib import Path

from azure.storage.blob import ContainerClient
from elastic.model import (
    CaseLawChunk,
    CaseLawDocument,
    Chunk,
    LegalDocument,
    WerkInstructieChunk,
    WerkInstructieDocument,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llm.llm import bulk_embed, get_embedding
from models import (
    CaseLawDocumentIngest,
    LegalDocumentIngest,
    WerkInstructieDocumentIngest,
)

logger = logging.getLogger(__name__)

SPLITTER = RecursiveCharacterTextSplitter()

STORAGE_LOCATIONS = {
    "law": "laws/articles",
    "case-law": "laws/case_law",
    "werk-instructie": "werk_instructie",
}

INGESTORS = {
    "law": LegalDocumentIngest,
    "case-law": CaseLawDocumentIngest,
    "werk-instructie": WerkInstructieDocumentIngest,
}


def chunk_document(text) -> list[str]:
    return [chunk.page_content for chunk in SPLITTER.create_documents([text])]


async def ingest_document(title, body, url, date, law_name):
    logger.info(f"Ingesting document: {title}, {body} from {law_name}")
    legal_document = LegalDocument(
        title=title, body=body, url=url, date=date, law_name=law_name
    )
    await legal_document.save()

    chunks = chunk_document(body)
    logger.info(f"Chunked document into {len(chunks)} chunks")
    for index, chunk_text in enumerate(chunks):
        chunk = Chunk(
            document_id=legal_document.meta.id,
            chunk_index=index,
            chunk_text=chunk_text,
            law_name=law_name,
        )
        chunk.embedding = await get_embedding(chunk_text)
        await chunk.save()


async def bulk_ingest(documents, doc_type: str):
    async def make_async(iterable):
        for item in iterable:
            yield item

    if doc_type == "law":
        docs = [
            LegalDocument(
                title=title,
                body=body,
                url=url,
                date=date,
                law_name=law_name,
                meta={"id": str(uuid.uuid4())},
            )
            for title, body, url, date, law_name in documents
        ]
    elif doc_type == "case-law":
        docs = [
            CaseLawDocument(
                title=title,
                url=url,
                instantie=instantie,
                datum_uitspraak=datum_uitspraak,
                datum_publicatie=datum_publicatie,
                zaaknummer=zaaknummer,
                rechtsgebieden=rechtsgebieden,
                bijzondere_kenmerken=bijzondere_kenmerken,
                inhoudsindicatie=inhoudsindicatie,
                wetsverwijzingen=wetsverwijzingen,
                vindplaatsen=vindplaatsen,
                verrijkte_uitspraak=verrijkte_uitspraak,
                uitspraak=uitspraak,
                meta={"id": str(uuid.uuid4())},
            )
            for (
                title,
                url,
                instantie,
                datum_uitspraak,
                datum_publicatie,
                zaaknummer,
                rechtsgebieden,
                bijzondere_kenmerken,
                inhoudsindicatie,
                wetsverwijzingen,
                vindplaatsen,
                verrijkte_uitspraak,
                uitspraak,
            ) in documents
        ]
    elif doc_type == "werk-instructie":
        docs = [
            WerkInstructieDocument(
                title=title,
                subtitle=subtitle,
                publication_date=publication_date,
                url=url,
                body=body,
                meta={"id": str(uuid.uuid4())},
            )
            for (
                title,
                url,
                subtitle,
                publication_date,
                body,
            ) in documents
        ]
    else:
        raise ValueError(f"Invalid doc_type: {doc_type}")
    logger.info(f"Bulk ingesting {len(docs)} documents")

    if doc_type == "law":
        await LegalDocument.bulk(make_async(docs))
        chunks: list[Chunk] = []
        for doc in docs:
            logger.info(f"Chunking document {doc.meta.id}, {doc.title}")
            chunks.extend(
                [
                    Chunk(
                        document_id=doc.meta.id,
                        chunk_index=index,
                        chunk_text=chunk_text,
                        law_name=doc.law_name,
                    )
                    for index, chunk_text in enumerate(chunk_document(doc.body))
                ]
            )
    elif doc_type == "case-law":
        await CaseLawDocument.bulk(make_async(docs))
        chunks: list[CaseLawChunk] = []
        for doc in docs:
            logger.info(f"Chunking document {doc.meta.id}, {doc.title}")
            chunks.extend(
                [
                    CaseLawChunk(
                        document_id=doc.meta.id,
                        chunk_index=index,
                        chunk_text=chunk_text,
                        title=doc.title,
                    )
                    for index, chunk_text in enumerate(chunk_document(doc.uitspraak))
                ]
            )
    elif doc_type == "werk-instructie":
        await WerkInstructieDocument.bulk(make_async(docs))
        chunks: list[WerkInstructieChunk] = []
        for doc in docs:
            logger.info(f"Chunking document {doc.meta.id}, {doc.title}")
            chunks.extend(
                [
                    WerkInstructieChunk(
                        document_id=doc.meta.id,
                        chunk_index=index,
                        chunk_text=chunk_text,
                        title=doc.title,
                    )
                    for index, chunk_text in enumerate(chunk_document(doc.body))
                ]
            )

    embeddings = await bulk_embed([chunk.chunk_text for chunk in chunks])
    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding

    if doc_type == "law":
        await Chunk.bulk(make_async(chunks))
    elif doc_type == "case-law":
        await CaseLawChunk.bulk(make_async(chunks))
    elif doc_type == "werk-instructie":
        await WerkInstructieChunk.bulk(make_async(chunks))


async def ingest_from_blob_storage(
    container_name: str,
    doc_type: str,
) -> int:
    container_client = ContainerClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING"), container_name
    )
    blobs = container_client.list_blobs()

    def _get_ingest_type(blob):
        if doc_type == "law":
            return LegalDocumentIngest(
                **json.loads(container_client.download_blob(blob).readall())
            )
        elif doc_type == "case-law":
            return CaseLawDocumentIngest(
                **json.loads(container_client.download_blob(blob).readall())
            )
        elif doc_type == "werk-instructie":
            return WerkInstructieDocumentIngest(
                **json.loads(container_client.download_blob(blob).readall())
            )
        else:
            raise ValueError(f"Invalid doc_type: {doc_type}")

    json_documents = [
        _get_ingest_type(blob) for blob in blobs if blob.name.endswith(".json")
    ]
    if doc_type == "law":
        await bulk_ingest(
            (
                (doc.title, doc.body, doc.url, doc.date, doc.law_name)
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    elif doc_type == "case-law":
        await bulk_ingest(
            (
                (
                    doc.title,
                    doc.url,
                    doc.instantie,
                    doc.datum_uitspraak,
                    doc.datum_publicatie,
                    doc.zaaknummer,
                    doc.rechtsgebieden,
                    doc.bijzondere_kenmerken,
                    doc.inhoudsindicatie,
                    doc.wetsverwijzingen,
                    doc.vindplaatsen,
                    doc.verrijkte_uitspraak,
                    doc.uitspraak,
                )
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    elif doc_type == "werk-instructie":
        await bulk_ingest(
            (
                (doc.title, doc.url, doc.subtitle, doc.publication_date, doc.body)
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    else:
        raise ValueError(f"Invalid doc_type: {doc_type}")

    return len(json_documents)


def load_from_local_storage(path: Path) -> list[dict]:
    """Load JSON documents from local storage."""
    if not path.exists():
        raise FileNotFoundError(f"Path {path} does not exist")

    json_documents = []
    for file in path.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            json_documents.append(json.load(f))

    return json_documents


async def ingest_from_local_storage(
    doc_type: str,
) -> int:

    def _get_ingest_type(json_file):
        if not doc_type in INGESTORS.keys():
            raise ValueError(f"Invalid doc_type: {doc_type}")
        else:
            # return INGESTORS[doc_type](load_from_local_storage(file_path))
            return INGESTORS[doc_type](**json_file)

    file_path = (
        Path("__file__").parent.parent.parent
        / "/scrapers"
        / STORAGE_LOCATIONS[doc_type]
    )
    logger.info(f"Loading JSON documents from {file_path} for doc_type {doc_type}")

    json_documents = [
        _get_ingest_type(json_file) for json_file in load_from_local_storage(file_path)
    ]

    if doc_type == "law":
        await bulk_ingest(
            (
                (doc.title, doc.body, doc.url, doc.date, doc.law_name)
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    elif doc_type == "case-law":
        await bulk_ingest(
            (
                (
                    doc.title,
                    doc.url,
                    doc.instantie,
                    doc.datum_uitspraak,
                    doc.datum_publicatie,
                    doc.zaaknummer,
                    doc.rechtsgebieden,
                    doc.bijzondere_kenmerken,
                    doc.inhoudsindicatie,
                    doc.wetsverwijzingen,
                    doc.vindplaatsen,
                    doc.verrijkte_uitspraak,
                    doc.uitspraak,
                )
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    elif doc_type == "werk-instructie":
        await bulk_ingest(
            (
                (doc.title, doc.url, doc.subtitle, doc.publication_date, doc.body)
                for doc in json_documents
            ),
            doc_type=doc_type,
        )
    else:
        raise ValueError(f"Invalid doc_type: {doc_type}")

    return len(json_documents)
