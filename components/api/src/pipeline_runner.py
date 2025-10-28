import httpx
from models import (
    ChatQuery,
    PipelineDataCollection,
    VectorSearchCaseLawResult,
    VectorSearchResult,
    VectorSearchWerkInstructieResult,
)
from services.db_service import search_selectielijsten
from services.kg_service import (
    encode_bwb_uri,
    extract_bwbr_and_article,
    get_article_uri,
    query_graph_lawuri,
    query_taxonomy,
)
from services.llm_service import extract_sources_in_answer, get_answer_llm, get_prompt
from services.rag_service import (
    search_case_law,
    search_law_article,
    search_werk_instructie,
)
from sqlalchemy.orm import Session


async def query_graphs(
    urls: list[str],
    http_client: httpx.AsyncClient,
    query_jas=True,
) -> tuple[list[str], list[dict], list[dict]]:
    lido_uris: list[str] = []
    lido_results: list[dict] = []
    jas_results: list[dict] = []
    for url in urls:
        bwbr, artikel = extract_bwbr_and_article(url)
        lido_uri = await get_article_uri(bwbr, artikel, http_client)
        if lido_uri:
            if query_jas:
                jas_uri = encode_bwb_uri(lido_uri)
                jas_results.append(
                    await query_graph_lawuri(jas_uri, "jas", http_client)
                )
            else:
                jas_results = []

            lido_uris.append(lido_uri)
            lido_results.append(await query_graph_lawuri(lido_uri, "lido", http_client))
        else:
            lido_uris.append("")
            lido_results.append("")

    return lido_uris, lido_results, jas_results


async def run_pipeline(
    chat_query: ChatQuery, db: Session, http_client: httpx.AsyncClient
) -> dict[str, dict]:
    """Run the pipeline for the given chat query"""

    data_sources = await collect_data_sources(chat_query, db, http_client)

    # Step 4: Format prompt for LLM
    prompt = await get_prompt(chat_query.message, data_sources)

    # Step 5: Query the LLM
    response = await get_answer_llm(prompt)

    referenced_response = await extract_sources_in_answer(
        response["message"], data_sources
    )

    return referenced_response


async def collect_data_sources(
    chat_query: ChatQuery, db: Session, http_client: httpx.AsyncClient
) -> dict[str, list[str]]:
    """Collect data sources for the given chat query"""

    # Step 1: Perform RAG search
    vector_search_result = await search_law_article(chat_query=chat_query)
    if isinstance(vector_search_result, str):
        vector_search_result = VectorSearchResult(
            documents=[],
            chunks=[],
            titles=[],
            laws=[],
            urls=[],
        )

    case_law_search_result = await search_case_law(chat_query=chat_query)
    if isinstance(case_law_search_result, str):
        case_law_search_result = VectorSearchCaseLawResult(
            documents=[],
            chunks=[],
            case_numbers=[],
            titles=[],
            inhoudsindicaties=[],
            date_uitspraken=[],
            urls=[],
        )
    werk_instructie_search_result = await search_werk_instructie(chat_query=chat_query)
    if isinstance(werk_instructie_search_result, str):
        werk_instructie_search_result = VectorSearchWerkInstructieResult(
            documents=[],
            chunks=[],
            titles=[],
            urls=[],
        )
    # Step 2: Perform DB search to find relevant rows based on user query
    selectielijsten_result = await search_selectielijsten(chat_query.message, db)
    if isinstance(selectielijsten_result, str):
        selectielijsten_result = []

    # Step 3: Perform KG search to find relevant taxonomy terms
    taxonomy_result = await query_taxonomy(chat_query.message, "Taxonomy", http_client)

    pipeline_data = PipelineDataCollection(
        documents=vector_search_result.documents,
        chunks=vector_search_result.chunks,
        titles=vector_search_result.titles,
        laws=vector_search_result.laws,
        urls=vector_search_result.urls,
        case_law_documents=case_law_search_result.documents,
        case_law_chunks=case_law_search_result.chunks,
        case_law_titles=case_law_search_result.titles,
        case_law_inhoudsindicaties=case_law_search_result.inhoudsindicaties,
        case_law_date_uitspraken=case_law_search_result.date_uitspraken,
        case_law_case_numbers=case_law_search_result.case_numbers,
        case_law_urls=case_law_search_result.urls,
        werk_instructie_documents=werk_instructie_search_result.documents,
        werk_instructie_chunks=werk_instructie_search_result.chunks,
        werk_instructie_titles=werk_instructie_search_result.titles,
        werk_instructie_urls=werk_instructie_search_result.urls,
        uris=[],
        lido_results=[],
        jas_results=[],
        case_law_uris=[],
        case_law_lido_results=[],
        selectielijsten_result=selectielijsten_result,
        taxonomy_result=taxonomy_result,
    )

    # Step 4: Query JAS and LIDO graphs based on retrieved law articles
    # First, query the graphs for the vector search results:
    law_uris, law_lido, law_jas = await query_graphs(pipeline_data.urls, http_client)
    pipeline_data.uris.extend(law_uris)
    pipeline_data.lido_results.extend(law_lido)
    pipeline_data.jas_results.extend(law_jas)

    # Next, query the graphs for the case law search results:
    case_law_uris, case_law_lido, _ = await query_graphs(
        pipeline_data.case_law_urls, http_client, query_jas=False
    )
    pipeline_data.case_law_uris.extend(case_law_uris)
    pipeline_data.case_law_lido_results.extend(case_law_lido)

    if not any(
        [
            pipeline_data.documents,
            pipeline_data.case_law_documents,
            pipeline_data.werk_instructie_documents,
            pipeline_data.selectielijsten_result,
            pipeline_data.taxonomy_result,
            pipeline_data.uris,
            pipeline_data.case_law_uris,
        ]
    ):
        raise ValueError(
            "Kon geen bronnen vinden voor uw vraag, wees alstublieft specifieker."
        )
    return dict(pipeline_data)
