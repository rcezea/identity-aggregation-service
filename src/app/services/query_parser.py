import re

COUNTRY_MAP = {
    "nigeria": "NG",
    "angola": "AO",
    "kenya": "KE",
}

AGE_KEYWORDS = {
    "young": {"min_age": 16, "max_age": 24},
    "teenager": {"age_group": "teenager"},
    "teenagers": {"age_group": "teenager"},
    "adult": {"age_group": "adult"},
    "adults": {"age_group": "adult"},
}

GENDER_KEYWORDS = {
    "male": "male",
    "males": "male",
    "female": "female",
    "females": "female",
}


def parse_query(q: str) -> dict:
    q = q.lower()
    filters = {}

    # --- gender ---
    for word, value in GENDER_KEYWORDS.items():
        if word in q:
            filters["gender"] = value

    # --- age keywords ---
    for word, mapping in AGE_KEYWORDS.items():
        if word in q:
            filters.update(mapping)

    # --- "above X" ---
    match = re.search(r"(above|over)\s+(\d+)", q)
    if match:
        filters["min_age"] = int(match.group(2))

    # --- "below X" ---
    match = re.search(r"(below|under)\s+(\d+)", q)
    if match:
        filters["max_age"] = int(match.group(2))

    # --- country ---
    for name, code in COUNTRY_MAP.items():
        if f"from {name}" in q:
            filters["country_id"] = code

    return filters


def parse_or_error(q: str):
    if not q or not q.strip():
        return {
            "status": "error",
            "message": "Missing or empty parameter"
        }

    filters = parse_query(q)

    if not filters:
        return {
            "status": "error",
            "message": "Unable to interpret query"
        }

    return {"status": "ok", "filters": filters}
