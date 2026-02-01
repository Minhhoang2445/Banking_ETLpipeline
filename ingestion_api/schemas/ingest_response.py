from pydantic import BaseModel


class IngestResponse(BaseModel):
    batch_id: str
    rows: int
