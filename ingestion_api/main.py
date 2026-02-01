from fastapi import FastAPI
from routers.ingest import router as ingest_router

app = FastAPI(title="Ingestion API")

app.include_router(ingest_router)
