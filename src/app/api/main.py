# main.py
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.app.database import get_db, Session, Base, engine
from src.app.models import User
from src.app.services.data_processing import serialize, serializer
from src.app.services.data_validation import validate
from src.app.services.external_apis import fetch_api, ExternalAPIError
from src.app.services.query_parser import parse_or_error
from src.app.services.query_processing import (get_queries,
                                               apply_sort,
                                               apply_pagination)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield  # app runs here


api = FastAPI(lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
)


@api.exception_handler(ExternalAPIError)
async def external_api_error_handler(request: Request, exc: ExternalAPIError):
    return JSONResponse(
        status_code=502,
        content={
            "status": "error",
            "message": f"{exc.api_name} returned an invalid response"
        }
    )


@api.post("/api/profiles")
async def create_profile(body: dict, db: Session = Depends(get_db)):
    name: str = body.get("name")

    if not isinstance(name, str):
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid type"
            }
        )

    if not name or not name.strip():
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Missing or empty name"
            }
        )

    name = name.strip().lower()

    # Check that input is a String
    if not re.fullmatch(r"^[A-Za-z]+([ '-][A-Za-z]+)*$", name):
        return JSONResponse(
            status_code=422,
            content={
                "status":
                    "error",
                "message":
                    "Invalid type"
            }
        )

    # Check if name exists in database
    existing = db.query(User).filter(User.name == name).first()
    if existing:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Profile already exists",
                "data": serializer(existing)
            }
        )

    # Asynchronous API calls
    data = await fetch_api(name=name)

    # Data Validation
    validate(*data)

    # Data Processing
    data = serialize(*data)

    # Save data in database
    try:
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "data": serializer(user)
            }
        )
    except IntegrityError:
        db.rollback()
        existing = db.query(User).filter(User.name == name).first()
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Profile already exists",
                "data": serializer(existing)
            }
        )


# @api.get("/api/profiles/{id}", status_code=status.HTTP_200_OK)
async def get_profile_by_id(id: str, db: Session = Depends(get_db)):
    # Check if name exists in database
    existing = db.query(User).filter(User.id == id).first()
    if existing:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": serializer(existing)
            }
        )
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Profile not found"
        })


@api.get("/api/profiles", status_code=status.HTTP_200_OK)
async def list_profiles(
        request: Request,
        db: Session = Depends(get_db),
        sort_by: str = None,
        order: str = None,
        page: int = 1,
        limit: int = 10
):
    # Advanced Filtering & Sorting
    params = request.query_params
    conditions = get_queries(params, User)

    query = db.query(User).filter(*conditions)
    sort = apply_sort(query, User, sort_by, order)
    if sort.get("status") == "error":
        return sort

    query = sort["query"]
    query = apply_pagination(query, page=page, limit=limit)

    results = query.all()

    if not results:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "Profile not found"
            }
        )
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "page": page,
            "limit": limit if limit < 50 else 50,
            "total": len(results),
            "data": [
                {
                    "id": user.id,
                    "name": user.name,
                    "gender": user.gender,
                    "age": user.age,
                    "age_group": user.age_group,
                    "country_id": user.country_id,
                }
                for user in results
            ]
        }
    )


@api.get("/api/profiles/search")
def search_profiles(
        q: str,
        sort_by: str = None,
        order: str = None,
        page: int = Query(1, ge=1),
        limit: int = Query(20, le=100),
        db: Session = Depends(get_db),
):
    parsed = parse_or_error(q)

    if parsed.get("status") == "error":
        return parsed

    filters = parsed["filters"]

    conditions = get_queries(filters, User)
    query = db.query(User).filter(*conditions)
    sort = apply_sort(query, User, sort_by, order)
    if sort.get("status") == "error":
        return sort

    query = sort["query"]
    query = apply_pagination(query, page, limit)

    results = query.all()

    if not results:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "Profile not found"
            }
        )
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "page": page,
            "limit": limit if limit < 50 else 50,
            "total": len(results),
            "data": [
                {
                    "id": user.id,
                    "name": user.name,
                    "gender": user.gender,
                    "age": user.age,
                    "age_group": user.age_group,
                    "country_id": user.country_id,
                }
                for user in results
            ]
        }
    )


@api.delete("/api/profiles/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(id: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.id == id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {}
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Profile not found"
        })


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
