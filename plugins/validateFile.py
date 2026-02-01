import hashlib
import os
from sqlalchemy import create_engine, text
import os


class FileValidator:

    def __init__(self):
        db_url = os.getenv("DW_CONN_STRING")
        self.engine = create_engine(db_url)

    def create_table_if_not_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS file_ingestion_log (
            id SERIAL PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            file_size BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.engine.begin() as conn:
            conn.execute(text(query))

    def calculate_hash(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def validate_and_register(self, file_path: str):
        self.create_table_if_not_exists()

        file_hash = self.calculate_hash(file_path)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        with self.engine.begin() as conn:
            result = conn.execute(
                text("SELECT 1 FROM file_ingestion_log WHERE file_hash = :hash"),
                {"hash": file_hash}
            ).fetchone()

            if result:
                raise ValueError("❌ File already ingested (duplicate content)")

            conn.execute(
                text("""
                    INSERT INTO file_ingestion_log (file_name, file_hash, file_size)
                    VALUES (:name, :hash, :size)
                """),
                {
                    "name": file_name,
                    "hash": file_hash,
                    "size": file_size
                }
            )
