import datetime
from pathlib import Path


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