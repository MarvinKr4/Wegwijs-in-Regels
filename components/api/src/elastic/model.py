from elasticsearch_dsl import AsyncDocument, Date, DenseVector, Integer, Keyword, Text
from llm.llm import VECTOR_DIMS


class LegalDocument(AsyncDocument):
    class Index:
        name = "legal-documents"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    title = Text(analyzer="dutch")
    body = Text(analyzer="dutch")
    url = Keyword()
    date = Date()
    law_name = Text(analyzer="dutch")


class CaseLawDocument(AsyncDocument):
    class Index:
        name = "case-laws"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    title = Text(analyzer="dutch")
    url = Keyword()
    instantie = Text(analyzer="dutch")
    datum_uitspraak = Date()
    datum_publicatie = Date()
    zaaknummer = Keyword()
    formele_relaties = Keyword()
    rechtsgebieden = Keyword()
    bijzondere_kenmerken = Text(analyzer="dutch")
    inhoudsindicatie = Text(analyzer="dutch")
    wetsverwijzingen = Keyword(multi=True)
    vindplaatsen = Keyword(multi=True)
    verrijkte_uitspraak = Keyword()
    uitspraak = Text(analyzer="dutch")


class WerkInstructieDocument(AsyncDocument):
    class Index:
        name = "werk-instructie"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    title = Text(analyzer="dutch")
    subtitle = Text(analyzer="dutch")
    url = Keyword()
    publication_date = Date()
    body = Text(analyzer="dutch")


class Chunk(AsyncDocument):
    class Index:
        name = "chunks"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    document_id = Keyword(index=True)
    chunk_index = Integer(index=False)
    chunk_text = Text(index=False)
    embedding = DenseVector(dims=VECTOR_DIMS, similarity="cosine")
    law_name = Text(index=True)


class CaseLawChunk(AsyncDocument):
    class Index:
        name = "case-law-chunks"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    document_id = Keyword(index=True)
    chunk_index = Integer(index=False)
    chunk_text = Text(index=False)
    embedding = DenseVector(dims=VECTOR_DIMS, similarity="cosine")
    title = Text(analyzer="dutch")


class WerkInstructieChunk(AsyncDocument):
    class Index:
        name = "werk-instructie-chunks"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Meta:
        dynamic = True

    document_id = Keyword(index=True)
    chunk_index = Integer(index=False)
    chunk_text = Text(index=False)
    embedding = DenseVector(dims=VECTOR_DIMS, similarity="cosine")
    title = Text(analyzer="dutch")


async def create_indices():
    for cls in AsyncDocument.__subclasses__():
        await cls.init()
