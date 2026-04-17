# main.py
import re

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.app.services.data_processing import serialize
from src.app.services.external_apis import fetch_api, ExternalAPIError
from src.app.services.data_validation import validate

api = FastAPI()

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


@api.post("/api/profiles", status_code=status.HTTP_201_CREATED)
async def get_profiles(body: dict):
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

    data = await fetch_api(name=name)

    # data validation
    validate(*data)

    # data processing
    data = serialize(*data)
    return data


@api.get("/api/profiles/{id}", status_code=status.HTTP_200_OK)
async def get_profile_by_id(id: int):
    return {"message": f"Object {id} not found"}


@api.get("/api/profiles", status_code=status.HTTP_200_OK)
async def get_profiles():
    pass


@api.delete("/api/profiles/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(id: int):
    return None


if "__main__" == __name__:
    import uvicorn

    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
