import ast
import datetime
import json
import logging
import re
from collections import defaultdict, deque
from typing import Tuple

logger = logging.getLogger(__name__)


def consolidate_source_dict(data: dict) -> dict:
    """Remove indices from the source extraction dictionary and consilidate to one dictionary"""
    try:
        sources = []
        for dct in data["selectielijsten"]:
            dct["value"].pop("indices", None)
            sources.append(dct)

        law_type = ["laws", "case_laws"]
        for key in law_type:
            for dct in data[key]:
                dct["value"].pop("index", None)
                sources.append(dct)

        for dct in data["werkinstructies"]:
            dct["value"].pop("index", None)
            sources.append(dct)

        for dct in data["taxonomy"]:
            dct["value"].pop("index", None)
            sources.append(dct)

        return sources
    except Exception as e:
        logger.error(f"An error occurred while consolidating source dict: {e}")


def map_paragraph_sources(sources_indices: dict, sources_lst: dict) -> dict:
    try:
        sources = []
        paragraph, sources_lst = map_taxonomy_terms(sources_indices, sources_lst)
        law_sources, sources_lst = map_law_sources(sources_indices, sources_lst)
        case_law_sources, sources_lst = map_case_law_sources(
            sources_indices, sources_lst
        )
        werkinstructie_sources, sources_lst = map_werkinstructie_sources(
            sources_indices, sources_lst
        )
        selectielijsten_sources, sources_lst = map_selectielijsten_sources(
            sources_indices, sources_lst
        )
        if law_sources:
            sources.extend(law_sources)
        if case_law_sources:
            sources.extend(case_law_sources)
        if werkinstructie_sources:
            sources.extend(werkinstructie_sources)
        if selectielijsten_sources:
            sources.extend(selectielijsten_sources)

        # Remove duplicates in sources list
        sources = list(dict.fromkeys(sources))

        paragraph_sources_dict = {"paragraph": paragraph, "sources": sources}
        return paragraph_sources_dict
    except Exception as e:
        logger.error(f"An error occurred while mapping sources in paragraph: {e}")
        raise


def map_selectielijsten_sources(
    sources_indices: dict, sources_lst: dict
) -> Tuple[list, dict]:
    """Identifying selectielijsten sources in the paragraph and updating isSource to True for used sources."""
    try:
        if "INDEX_SELECTIELIJSTEN" in sources_indices:
            selectielijsten_sources = []
            if sources_indices["INDEX_SELECTIELIJSTEN"]:
                logger.info("Found selectielijsten source in paragraph")
                for idx in sources_indices["INDEX_SELECTIELIJSTEN"]:
                    if idx >= len(sources_lst["selectielijsten"]):
                        logger.warning(
                            f"Index {idx} is out of range for selectielijsten list"
                        )
                        continue
                    for i, dct in enumerate(sources_lst["selectielijsten"]):
                        if idx in dct["value"]["indices"]:
                            id = dct["id"]
                            selectielijsten_sources.append(id)
                            index_in_indices = dct["value"]["indices"].index(idx)
                            sources_lst["selectielijsten"][i]["value"]["rows"][
                                index_in_indices
                            ]["isSource"] = True
            else:
                logger.info("No selectielijsten source found in paragraph")

            return selectielijsten_sources, sources_lst
        else:
            return [], sources_lst
    except Exception as e:
        logger.error(f"An error occurred while mapping selectielijsten sources: {e}")


def map_law_sources(sources_indices: dict, sources_lst: dict) -> Tuple[list, dict]:
    """Identifying law and case law sources in the paragraph and updating isSource to True for used sources."""
    try:
        if "INDEX_WETTEN" in sources_indices:
            law_sources = []
            if sources_indices["INDEX_WETTEN"]:
                logger.info("Found laws source in paragraph")
                for idx in sources_indices["INDEX_WETTEN"]:
                    if idx >= len(sources_lst["laws"]):
                        logger.warning(f"Index {idx} is out of range for laws list")
                        continue
                    assert sources_lst["laws"][idx]["value"]["index"] == idx
                    id = sources_lst["laws"][idx]["id"]
                    law_sources.append(id)
                    sources_lst["laws"][idx]["value"]["isSource"] = True
            else:
                logger.info("No laws source found in paragraph")

            return law_sources, sources_lst
        else:
            return [], sources_lst
    except Exception as e:
        logger.error(f"An error occurred while mapping law sources: {e}")


def map_case_law_sources(sources_indices: dict, sources_lst: dict) -> Tuple[list, dict]:
    """Identifying law and case law sources in the paragraph and updating isSource to True for used sources."""
    try:
        if "INDEX_JURISPRUDENTIE" in sources_indices:
            law_sources = []
            if sources_indices["INDEX_JURISPRUDENTIE"]:
                logger.info("Found laws source in paragraph")
                for idx in sources_indices["INDEX_WETTEN"]:
                    idx = 0
                    assert sources_lst["case_laws"][idx]["value"]["index"] == idx
                    id = sources_lst["case_laws"][idx]["id"]
                    law_sources.append(id)
                    sources_lst["case_laws"][idx]["value"]["isSource"] = True
            else:
                logger.info("No case laws source found in paragraph")

            return law_sources, sources_lst
        else:
            return [], sources_lst
    except Exception as e:
        logger.error(f"An error occurred while mapping case law sources: {e}")


def map_werkinstructie_sources(
    sources_indices: dict, sources_lst: dict
) -> Tuple[list, dict]:
    """Identifying werkinstructie sources in the paragraph and updating isSource to True for used sources."""
    try:
        if "INDEX_WERKINSTRUCTIES" in sources_indices:
            werkinstructie_sources = []
            if sources_indices["INDEX_WERKINSTRUCTIES"]:
                logger.info("Found werkinstructie source in paragraph")
                for idx in sources_indices["INDEX_WERKINSTRUCTIES"]:
                    idx = 0  # NOTE: werk instructie document too big, it often gets it wrong, althought there is currently only one
                    assert sources_lst["werkinstructies"][idx]["value"]["index"] == idx
                    id = sources_lst["werkinstructies"][idx]["id"]
                    werkinstructie_sources.append(id)
                    sources_lst["werkinstructies"][idx]["value"]["isSource"] = True

            else:
                logger.info("No werkinstructie source found in paragraph")
            return werkinstructie_sources, sources_lst
        else:
            return [], sources_lst
    except Exception as e:
        logger.error(f"An error occurred while mapping werkinstructie sources: {e}")


def map_taxonomy_terms(sources_indices, sources_lst) -> Tuple[str, dict]:
    """Source indices to the unique source indices in sources dict and update isSource for used sources.
    Return paragraph with updated source id in angle brackets, eg. <persoonsgegevens> -> <source_5>
    """
    try:
        if "TERM_INDEX" in sources_indices:
            paragraph = sources_indices["PARAGRAPH"]
            if sources_indices["TERM_INDEX"]:
                # Ensure TERM_INDEX and CONTEXT_INDEX have the same length, most taxonomy terms only have 1 context so assume first
                if len(sources_indices["TERM_INDEX"]) != len(
                    sources_indices["CONTEXT_INDEX"]
                ):
                    while len(sources_indices["CONTEXT_INDEX"]) < len(
                        sources_indices["TERM_INDEX"]
                    ):
                        sources_indices["CONTEXT_INDEX"].append(0)
                for i, term_index in enumerate(sources_indices["TERM_INDEX"]):
                    if f"<{term_index}>" not in paragraph:
                        logger.info(f"Term index <{term_index}> not found in paragraph")
                        continue
                    else:
                        logger.info("Mapping taxonomy term in paragraph")
                        context_index = sources_indices["CONTEXT_INDEX"][i]
                        term_value = sources_lst["taxonomy"][term_index]["value"]
                        id = term_value["context"][context_index]["id"]
                        sources_lst["taxonomy"][term_index]["value"]["context"][
                            context_index
                        ]["isSource"] = True
                        paragraph = re.sub(rf"<{term_index}>", f"<{id}>", paragraph)
                # Remove brackets with numbers not in TERM_INDEX
                paragraph = re.sub(
                    r"<(\d+)>",
                    lambda match: (
                        ""
                        if int(match.group(1)) not in sources_indices["TERM_INDEX"]
                        else match.group(0)
                    ),
                    paragraph,
                )
            else:
                paragraph = re.sub(r"<[^>]+>", "", paragraph)
                logger.info("No taxonomy term found in paragraph")
            return paragraph, sources_lst
    except Exception as e:
        logger.error(f"An error occurred while mapping taxonomy terms: {e}")


def get_sources_with_ids_list(data: dict) -> dict:
    """Generate a dictionary of sources with unique IDs"""
    try:
        # Format data to comply with output format
        selectielijsten = process_selectielijst(data)
        laws = process_laws(data)
        case_laws = process_laws(data, is_caselaw=True)
        werkinstructies = process_werkinstructies(data)
        taxonomy = process_taxonomy(data)

        len_sources = (
            len(selectielijsten)
            + len(laws)
            + len(case_laws)
            + len(werkinstructies)
            + sum(len(term["context"]) for term in taxonomy)
        )
        # Generate unique ids for each source
        unique_ids = [f"source_{i+1}" for i in range(len_sources)]
        unique_ids = deque(unique_ids)

        sources_lst = {}

        # Assign unique IDs while iterating through different sources
        laws_list = []
        for source in laws:
            laws_list.append(
                {"id": unique_ids.popleft(), "type": "law", "value": source}
            )
        sources_lst["laws"] = laws_list

        case_laws_list = []
        for source in case_laws:
            source["date_uitspraak"] = (
                source["date_uitspraak"].isoformat()
                if isinstance(source["date_uitspraak"], datetime.date)
                else source["date_uitspraak"]
            )
            case_laws_list.append(
                {"id": unique_ids.popleft(), "type": "case_law", "value": source}
            )
        sources_lst["case_laws"] = case_laws_list

        werkinstructies_list = []
        for source in werkinstructies:
            werkinstructies_list.append(
                {"id": unique_ids.popleft(), "type": "werkinstructie", "value": source}
            )
        sources_lst["werkinstructies"] = werkinstructies_list

        selectielijsten_list = []
        for source in selectielijsten:
            selectielijsten_list.append(
                {"id": unique_ids.popleft(), "type": "selectielijst", "value": source}
            )
        sources_lst["selectielijsten"] = selectielijsten_list

        taxonomy_list = []
        for term in taxonomy:
            for context in term["context"]:
                context["id"] = unique_ids.popleft()
            taxonomy_list.append({"type": "taxonomy", "value": term})
        sources_lst["taxonomy"] = taxonomy_list

        return sources_lst
    except Exception as e:
        logger.error(f"An error occurred while generating source IDs: {e}")
        raise


def process_laws(data: dict, is_caselaw: bool = False) -> list[dict]:
    """Process laws data and case law data into output format"""
    try:
        laws = []

        if is_caselaw:
            for i, _ in enumerate(data["case_law_titles"]):
                law_dict = {
                    "isSource": False,
                    "document": data["case_law_documents"][i],
                    "chunks": data["case_law_chunks"][i],
                    "title": data["case_law_titles"][i],
                    "inhoudsindicatie": data["case_law_inhoudsindicaties"][i],
                    "date_uitspraak": data["case_law_date_uitspraken"][i],
                    "url": data["case_law_urls"][i],
                    "lido": {},
                    "index": i,
                }
                laws.append(law_dict)
        else:
            for i, law in enumerate(data["laws"]):
                law_dict = {
                    "isSource": False,
                    "document": data["documents"][i],
                    "title": data["titles"][i],
                    "law": law,
                    "url": data["urls"][i],
                    "lido": {},
                    "index": i,
                }
                laws.append(law_dict)

        return laws
    except Exception as e:
        logger.error(f"An error occurred while processing laws data: {e}")


def process_werkinstructies(data: dict) -> list[dict]:
    try:
        werkinstructies = []
        for i, _ in enumerate(data["werk_instructie_titles"]):
            werkinstructie_dict = {
                "isSource": False,
                # "document": data["werk_instructie_documents"][i],
                "chunks": data["werk_instructie_chunks"][i],
                "title": data["werk_instructie_titles"][i],
                "url": data["werk_instructie_urls"][i],
                "index": i,
            }
            werkinstructies.append(werkinstructie_dict)
        return werkinstructies
    except Exception as e:
        logger.error(f"An error occurred while processing werkinstructie data: {e}")


def process_taxonomy(data) -> list[dict]:
    """Process taxonomy data into output format"""
    try:
        taxonomy = []

        for i, term in enumerate(data["taxonomy_result"]):
            term_dict = {
                "label": term["label"],
                "index": i,
                "context": [],
            }
            for i, val in enumerate(term["context"]):
                # NOTE: temporary fix for missing keys in context
                for key in ["source", "definition", "naderToegelicht", "wetcontext"]:
                    if key not in val:
                        val[key] = ""
                context_dict = {
                    "id": "",
                    "isSource": False,
                    "source": val["source"],
                    "definition": val["definition"],
                    "naderToegelicht": val["naderToegelicht"],
                    "wetcontext": {
                        "url": val["wetcontext"],
                    },
                }
                term_dict["context"].append(context_dict)
            taxonomy.append(term_dict)

        return taxonomy
    except Exception as e:
        logger.error(f"An error occurred while processing taxonomy data: {e}")


def process_selectielijst(data: dict) -> list[dict]:
    """Create output structure for selectielijsten"""
    try:
        grouped_data = defaultdict(lambda: {"name": "", "rows": [], "indices": []})

        for index, row in enumerate(data["selectielijsten_result"]):
            selectielijsten_name = row["selectielijsten"]
            new_row = row.copy()
            new_row["isSource"] = False

            grouped_data[selectielijsten_name]["name"] = selectielijsten_name
            grouped_data[selectielijsten_name]["rows"].append(new_row)
            grouped_data[selectielijsten_name]["indices"].append(index)

        selectielijsten_lst = list(grouped_data.values())
        return selectielijsten_lst
    except Exception as e:
        logger.error(f"An error occurred while processing selectielijst data: {e}")


def parse_source_extraction_from_llm(response: str) -> dict:
    """Parse the source extraction response and turn into a dictionary"""
    try:
        # Clean response and parse into a dictionary
        response = re.sub(
            r"^```[a-zA-Z0-9]*\n?", "", response
        )  # Remove starting ```json or similar
        response = re.sub(r"\n?```$", "", response)  # Remove trailing ```
        response = re.sub(r".*?{", "{", response)
        response = re.sub(r"}.*", "}", response)
        try:
            response_dict = ast.literal_eval(response)
        except (ValueError, SyntaxError):
            # If literal_eval fails, attempt to clean and retry
            logger.warning("Parsing failed, attempting to clean response")

            # Attempting some basic cleaning
            response = re.sub(
                r",\s*}", "}", response
            )  # Fix common issue of trailing commas before closing brace
            response = re.sub(
                r",\s*}", "}", response
            )  # Remove extra commas before closing brackets
            response = re.sub(
                r"(\w+)\s*:\s*([^\s,]+)[^\w\s,]", r'\1: "\2"', response
            )  # Ensure values are quoted

            # Try to parse again
            try:
                response_dict = ast.literal_eval(response)
            except (ValueError, SyntaxError):
                logger.error(f"Parsing failed again, attempting JSON parsing.")
                # If cleaning failed, attempt JSON parsing
                try:
                    response_dict = json.loads(response)
                except (ValueError, SyntaxError) as e:
                    logger.error(f"Error parsing response: {e}")
                    raise

        return response_dict
    except Exception as e:
        logger.error(f"An error occurred while parsing source extraction response: {e}")
        raise
