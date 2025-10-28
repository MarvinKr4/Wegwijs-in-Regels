import logging

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from http_client import get_http_client
from models import ChatQuery
from pipeline_runner import run_pipeline
from postgresql.database import get_db
from sqlalchemy.orm import Session
from system_api import router as system_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="API",
    description="Wegwijs in Regels API",
    version="1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)


@app.post("/chat")
async def query_pipeline(
    chat_query: ChatQuery,
    db: Session = Depends(get_db),
    http_client=Depends(get_http_client),
):
    """Query pipeline"""

    logger.info(f"Received query: {chat_query.message}")
    result = await run_pipeline(chat_query=chat_query, db=db, http_client=http_client)

    return {"message": result["response"]}


# NOTE: output not compatible with frontend yet
@app.post("/pipeline")
async def query_pipeline_data(
    chat_query: ChatQuery,
    db: Session = Depends(get_db),
    http_client=Depends(get_http_client),
):
    """Query pipeline"""
    logger.info(f"Received query: {chat_query.message}")
    result = await run_pipeline(chat_query=chat_query, db=db, http_client=http_client)
    return result


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )
