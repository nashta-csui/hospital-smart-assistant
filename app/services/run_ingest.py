"""
CLI script to ingest RAG documents into the database.

Usage:
    cd hospital-smart-assistant
    uv run python -m app.services.run_ingest

Requires:
    - PostgreSQL with pgvector running (docker compose up db -d)
    - DATABASE_URL environment variable set (or defaults to docker-compose settings)
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.services.ingest import ingest_documents


def main():
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        return

    engine = create_engine(settings.database_url)
    session = sessionmaker(bind=engine)()

    try:
        count = ingest_documents(session, data_dir)
        print(f"Successfully ingested {count} documents.")
    except Exception as e:
        print(f"ERROR: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
