import logging
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from llm.llm import invoke as invoke_llm
from models import VectorSearchResult

logger = logging.getLogger(__name__)

JINJA_ENV = Environment(
    enable_async=True, loader=FileSystemLoader(Path(__file__).parent / "templates")
)

RAG_TEMPLATE = JINJA_ENV.get_template("rag_template.jinja2")


async def formulate_rag_answer(
    question: str, vector_search_results: VectorSearchResult
) -> str:
    """Formulate an answer based on the question and vector search results

    Args:
        question (str): user question
        vector_search_results (VectorSearchResult):

    Returns:
        str: answer to the user question
    """
    rendered_template = await RAG_TEMPLATE.render_async(
        question=question,
        vector_search_results=vector_search_results,
        docs_chunks=enumerate(
            zip(
                vector_search_results.documents,
                vector_search_results.chunks,
                vector_search_results.titles,
                vector_search_results.laws,
                vector_search_results.urls,
            ),
            start=1,
        ),
    )
    logger.info(f"Rendered prompt template: {rendered_template}")

    response = await invoke_llm([("human", rendered_template)])

    answer, source_index = extract_answer_and_source(response)
    if answer is not None:
        return answer, source_index
    else:
        return response, None


def extract_answer_and_source(text):
    match = re.search(r"^(.*?)\s*\nBRON:[^\d]*(\d+)", text, re.DOTALL)
    if match:
        answer = match.group(1).strip()
        source_index = int(match.group(2))
        return answer, source_index
    return None, None
