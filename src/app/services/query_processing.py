from typing import Any
from sqlalchemy import asc, desc
from starlette.responses import JSONResponse

ALLOWED = {
    "gender": lambda m, v: m.gender == v,
    "age_group": lambda m, v: m.age_group == v,
    "country_id": lambda m, v: m.country_id == v,
    "min_age": lambda m, v: m.age >= v,
    "max_age": lambda m, v: m.age <= v,
    "min_gender_probability": lambda m, v: m.gender_probability >= v,
    "max_gender_probability": lambda m, v: m.gender_probability <= v,
}

CONTROL_PARAMS = {"sort_by", "order", "page", "limit"}

def get_queries(params, model) -> JSONResponse | list[Any]:
    invalid_keys = set(params.keys()) - set(ALLOWED.keys())
    invalid_keys = invalid_keys - set(CONTROL_PARAMS)
    if invalid_keys:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid query parameters"
            }
        )
    conditions = []

    for key, value in params.items():
        operator = ALLOWED.get(key)
        if operator:
            conditions.append(operator(model, value))

    return conditions


def apply_sort(query, model, sort: str | None, order: str | None = "asc"):

    if not sort:
        return query

    column = getattr(model, sort, None)
    if column is None:
        return query

    if order == "desc":
        return query.order_by(desc(column))

    return query.order_by(asc(column))


def apply_pagination(query, page: int = 1, limit: int = 10):
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    if limit > 50:
        limit = 50

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit)
