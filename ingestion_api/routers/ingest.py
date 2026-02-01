from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import tempfile
import os

from services.file_ingest_service import FileIngestService

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/file")
async def ingest_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    service = FileIngestService()

    if filename.endswith(".csv"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(file.file, tmp)
            csv_path = tmp.name
        csv_path = service.save_csv_to_data_dir(csv_path)

    elif filename.endswith(".xlsx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            excel_path = tmp.name

        csv_path = service.convert_excel_to_csv(excel_path)
        os.remove(excel_path)

    else:
        raise HTTPException(
            status_code=400,
            detail="Only CSV or Excel (.xlsx) files are supported"
        )

    service.trigger_airflow(csv_path)

    return {
        "message": "File ingested successfully (standardized to CSV)",
        "csv_path": csv_path
    }
