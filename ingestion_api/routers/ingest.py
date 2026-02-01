from fastapi import APIRouter, UploadFile, File
import shutil
import tempfile
import os

from services.file_ingest_service import FileIngestService

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/excel")
async def ingest_excel(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    service = FileIngestService()
    csv_path = service.convert_excel_to_csv(temp_path)

    os.remove(temp_path)

    service.trigger_airflow(csv_path)

    return {
        "message": "Convert Excel → CSV & trigger Airflow success",
        "csv_path": csv_path
    }
