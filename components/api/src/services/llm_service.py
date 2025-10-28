import asyncio
import logging
import re
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from llm.llm import invoke as invoke_llm
from services.utils import (
    consolidate_source_dict,
    get_sources_with_ids_list,
    map_paragraph_sources,
    parse_source_extraction_from_llm,
)

logger = logging.getLogger(__name__)

JINJA_ENV = Environment(
    enable_async=True, loader=FileSystemLoader(Path(__file__).parent / "templates")
)

PROMPT_TEMPLATE = JINJA_ENV.get_template("prompt_template.jinja2")
CONTEXT = "Een ambtenaar van het Nederlandse ministerie van Infrastructuur en Waterstaat met een juridische achtergrond behandelt een verzoek. De ambtenaar wil bepalen of de gezochte informatie verstrekt kan worden onder de Wet open overheid (WOO), of alle relevante bestanden met betrekking tot de vraag in het archief aanwezig zijn op basis van de Archiefwet 1995 en selectielijsten, en hoe er moet worden omgegaan met persoonsgegevens in de verstrekte informatie, rekening houdend met de Uitvoeringswet Algemene Verordening Gegevensbescherming."


async def get_answer_llm(prompt: str) -> dict[str, str]:
    """Invoke LLM with prompt"""
    response = await invoke_llm([("human", prompt)])
    logger.info(response)
    return {"message": response}


async def get_prompt(question: str, data: dict) -> str:
    try:
        rendered_template = await PROMPT_TEMPLATE.render_async(
            question=question,
            context=CONTEXT,
            sources=enumerate(
                zip(
                    data["documents"],
                    data["titles"],
                    data["laws"],
                    data["urls"],
                    data["uris"],
                    data["lido_results"],
                    data["jas_results"],
                ),
                start=0,
            ),
            case_law_sources=enumerate(
                zip(
                    data["case_law_titles"],
                    data["case_law_chunks"],
                    data["case_law_inhoudsindicaties"],
                    data["case_law_date_uitspraken"],
                    data["case_law_case_numbers"],
                    data["case_law_urls"],
                    data["case_law_lido_results"],
                ),
                start=0,
            ),
            werkinstructies=enumerate(
                zip(
                    data["werk_instructie_titles"],
                    data["werk_instructie_chunks"],
                    data["werk_instructie_urls"],
                ),
                start=0,
            ),
            selectielijsten=data["selectielijsten_result"],
            taxonomy=data["taxonomy_result"],
        )
        logger.info(f"Rendered prompt template: {rendered_template}")

        return rendered_template
    except Exception as e:
        logger.error(f"An error occurred while rendering the prompt template: {e}")
        raise


def get_paragraphs(response: str) -> list[str]:
    """Extract paragraphs from LLM response"""

    def clean_response(response: str) -> str:
        """Clean response from any special characters except comma, dot, and colon"""
        return re.sub(r"[^\w\s,.:*<>-]", "", response)

    response = clean_response(response)
    paragraphs = response.split("\n\n")
    return [p for p in paragraphs if p]


async def get_source_extraction_prompt(paragraph, source) -> dict:
    """Generate template for source extraction in per paragraph"""
    try:
        source_template = source[1]
        source_data = source[0]
        SOURCE_EXTRACTION_TEMPLATE = JINJA_ENV.get_template(source_template)
        rendered_template = await SOURCE_EXTRACTION_TEMPLATE.render_async(
            paragraph=paragraph, context=CONTEXT, source=source_data
        )
        logger.info(f"Rendered prompt template: {rendered_template}")

        return rendered_template
    except Exception as e:
        logger.error(
            f"An error occurred while rendering the source prompt template: {e}"
        )
        raise


async def process_sources(paragraph, source):
    prompt = await get_source_extraction_prompt(paragraph[1], source)
    source_response = await get_answer_llm(prompt)
    sources_indices = parse_source_extraction_from_llm(source_response["message"])
    sources_indices["paragraph_index"] = paragraph[0]
    return sources_indices


async def extract_sources_in_answer(response: str, data: dict) -> dict[list[dict]]:
    """Extract sources from each paragraph in the LLM response using LLM"""
    try:
        logger.info("Extracting sources used in LLM response")
        paragraphs = get_paragraphs(response)
        indexed_paragraphs = [
            (index, element) for index, element in enumerate(paragraphs)
        ]

        sources_lst = get_sources_with_ids_list(data)

        prepared_sources = prepare_sources(data)

        extracted_sources = []
        for source in prepared_sources:
            source = await asyncio.gather(
                *[
                    process_sources(paragraph, source)
                    for paragraph in indexed_paragraphs
                ]
            )
            extracted_sources.extend(source)

        sorted_paragraph_sources = merge_dicts_by_paragraph(extracted_sources)

        paragraphs_with_sources = []
        for paragraph in sorted_paragraph_sources:
            paragraphs_with_sources.append(
                map_paragraph_sources(paragraph, sources_lst)
            )

        logger.info("Sources extracted successfully")

        sources_lst = consolidate_source_dict(sources_lst)
        response_dict = {
            "answer": {"text": paragraphs_with_sources, "sources": sources_lst}
        }
        return response_dict
    except Exception as e:
        logger.error(
            f"An error occurred while extracting sources used in LLM response: {e}"
        )


def merge_dicts_by_paragraph(data):
    merged = defaultdict(dict)

    for entry in data:
        paragraph_index = entry["paragraph_index"]
        merged[paragraph_index].update(entry)

    return [merged[i] for i in sorted(merged)]


def prepare_sources(data: dict) -> list[tuple]:
    """Prepare sources for rendering in the prompt template"""
    sources = []

    if data["documents"]:
        law_source = enumerate(
            zip(
                data["documents"],
                data["titles"],
                data["laws"],
                data["urls"],
                data["uris"],
                data["lido_results"],
                data["jas_results"],
            ),
            start=0,
        )
        sources.append((law_source, "law_extraction.jinja2", "law"))

    if data["case_law_titles"]:
        case_law_sources = enumerate(
            zip(
                data["case_law_titles"],
                data["case_law_chunks"],
                data["case_law_inhoudsindicaties"],
                data["case_law_date_uitspraken"],
                data["case_law_case_numbers"],
                data["case_law_urls"],
                data["case_law_lido_results"],
            ),
            start=0,
        )
        sources.append((case_law_sources, "case_law_extraction.jinja2", "case_law"))

    if data["werk_instructie_titles"]:
        werkinstructies = enumerate(
            zip(
                data["werk_instructie_titles"],
                data["werk_instructie_chunks"],
                data["werk_instructie_urls"],
            ),
            start=0,
        )
        sources.append(
            (werkinstructies, "werkinstructie_extraction.jinja2", "werkinstructie")
        )

    if data["selectielijsten_result"]:
        sources.append(
            (
                data["selectielijsten_result"],
                "selectielijsten_extraction.jinja2",
                "selectielijsten",
            )
        )
    if data["taxonomy_result"]:
        sources.append(
            (data["taxonomy_result"], "taxonomie_extraction.jinja2", "taxonomy")
        )
    return sources
