from datetime import date
from typing import Any

from pydantic import BaseModel, field_validator


class ChatQuery(BaseModel):
    session_id: str
    message: str


class GraphUpload(BaseModel):
    dataset: str
    graph: str


class GraphFromBlobUpload(BaseModel):
    blob_name: str


class GraphLawQuery(BaseModel):
    lawuri: str
    graph: str


class GraphTaxonomyQuery(BaseModel):
    user_query: str
    graph: str = "Taxonomy"


class BlobStorageIngest(BaseModel):
    container_name: str = "legal-docs"
    doc_type: str = "law"


class LegalDocumentIngest(BaseModel):
    title: str
    body: str
    url: str
    date: date
    law_name: str

    @field_validator("date", mode="before")
    @classmethod
    def ensure_date(cls, v: Any):
        if not isinstance(v, date):
            v = date.fromisoformat(v)
        return v


class CaseLawDocumentIngest(BaseModel):
    title: str
    url: str
    instantie: str
    datum_uitspraak: date
    datum_publicatie: date
    zaaknummer: str
    formele_relaties: str = ""
    rechtsgebieden: str
    bijzondere_kenmerken: str
    inhoudsindicatie: str
    wetsverwijzingen: list[str]
    vindplaatsen: list[str]
    verrijkte_uitspraak: str
    uitspraak: str


class WerkInstructieDocumentIngest(BaseModel):
    title: str
    subtitle: str
    url: str
    publication_date: date
    body: str


class VectorSearchResult(BaseModel):
    documents: list[str]
    chunks: list[list[str]]
    titles: list[str]
    laws: list[str]
    urls: list[str]


class VectorSearchCaseLawResult(BaseModel):
    documents: list[str]
    chunks: list[list[str]]
    titles: list[str]
    inhoudsindicaties: list[str]
    date_uitspraken: list[date]
    case_numbers: list[str]
    urls: list[str]


class VectorSearchWerkInstructieResult(BaseModel):
    documents: list[str]
    chunks: list[list[str]]
    titles: list[str]
    urls: list[str]


class CSVFile(BaseModel):
    file_name: str


class PipelineDataCollection(BaseModel):
    documents: list[str]
    chunks: list[list[str]]
    titles: list[str]
    laws: list[str]
    urls: list[str]
    case_law_documents: list[str]
    case_law_chunks: list[list[str]]
    case_law_titles: list[str]
    case_law_inhoudsindicaties: list[str]
    case_law_date_uitspraken: list[date]
    case_law_case_numbers: list[str]
    case_law_urls: list[str]
    werk_instructie_documents: list[str]
    werk_instructie_chunks: list[list[str]]
    werk_instructie_titles: list[str]
    werk_instructie_urls: list[str]
    uris: list[str]
    lido_results: list[dict]
    jas_results: list[dict]
    case_law_uris: list[str]
    case_law_lido_results: list[dict]
    selectielijsten_result: list[dict] | list
    taxonomy_result: list[dict]
