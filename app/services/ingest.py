import datetime
from pathlib import Path
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.models.rag.chunk_dokumen import ChunkDokumen
from app.models.rag.dokumen import Dokumen
from app.services import get_embedding_model

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_documents(data_dir: Path) -> list[tuple[str, str]]:
    """
    Load all RAG_*.txt files from a directory.

    Returns a sorted list of (filename, text_content) tuples.
    Raises FileNotFoundError if directory doesn't exist.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    docs = []
    for txt_file in sorted(data_dir.glob("RAG_*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        docs.append((txt_file.name, text))
    return docs

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping chunks using recursive character splitting.

    Prefers splitting on paragraph boundaries (\\n\\n), then lines (\\n),
    then sentences (. ), then words ( ).
    """
    if not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def ingest_documents(db: Session, data_dir: Path) -> int:
    """
    Full ingestion pipeline: load RAG files, chunk, embed, store in DB.

    Returns the number of documents ingested.
    """
    model = get_embedding_model()
    docs = load_documents(data_dir)

    for filename, text in docs:
        doc = Dokumen(
            id=uuid4(),
            filename=filename,
            rawtext=text,
            uploaded_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(doc)
        db.flush()

        chunks = chunk_text(text)
        if not chunks:
            continue

        embeddings = model.encode(chunks)

        for content, embedding in zip(chunks, embeddings):
            chunk_record = ChunkDokumen(
                id=uuid4(),
                doc_id=doc.id,
                content=content,
                embedding=embedding.tolist(),
            )
            db.add(chunk_record)

    db.commit()
    return len(docs)
