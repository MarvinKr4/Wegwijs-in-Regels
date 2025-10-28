import logging

logger = logging.getLogger(__name__)

beg_sbb = "http://begrippen.nlbegrip.nl/sbb/id/concept/"
lido = "http://linkeddata.overheid.nl/terms/bwb/id#"
eurlex = "https://eur-lex.europa.eu/eli#"
wir = "http://www.koopoverheid.nl/WegwijsinRegels#"

LIST_PARAMS = [
    "naderToegelicht",
    "scopeNote",
    "NarrowerGeneric",
    "BroaderGeneric",
    "AltLabel",
    "opGrondVan",
]

OTHER_PARAMS = [
    "wetcontext",
]


def merge_json(data):
    merged = {}
    for concept in data:
        if not concept:
            logger.info("No concept found. Continuing.")
            continue

        for entry in concept:
            label = None
            context_index = None
            context_entry = {}

            try:

                concept = entry["concept"]["value"]
                label = entry["label"]["value"]

                if label not in merged:
                    merged[label] = {"concept": concept, "label": label, "context": []}
            except KeyError as e:
                logger.error(f"KeyError: {e}")

            try:
                source = entry["source"]["value"]

                for i, context in enumerate(merged[label]["context"]):
                    if source in context["source"]:
                        context_entry = context
                        context_index = i
                        break

                if not context_entry:
                    context_entry = {
                        "source": entry["source"]["value"],
                        "definition": entry["definition"]["value"],
                    }
            except KeyError as e:
                logger.error(f"KeyError: {e}")

            # Handle naderToegelicht as a list (if it exists)
            for param in LIST_PARAMS:
                if param in entry or param == "naderToegelicht":
                    if param not in context_entry:
                        context_entry[param] = list()
                    if param in entry:
                        param_val = entry[param]["value"]
                        if not param_val in context_entry[param]:
                            context_entry[param].append(param_val)

            # Handle other properties
            for param in OTHER_PARAMS:
                if param in entry:
                    if not param in context_entry.keys():
                        context_entry[param] = entry[param]["value"]
                    elif not entry[param]["value"] in context_entry[param]:
                        context_entry[param] = entry[param]["value"]

            if context_index is None:
                logger.info("No context index found. Appending context entry")
                merged[label]["context"].append(context_entry)
            else:
                logger.info(
                    f"Context index found. Updating context entry for {context_index=}"
                )
                merged[label]["context"][context_index] = context_entry

    return list(merged.values())
