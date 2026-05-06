from pathlib import Path


def load_documents(data_dir: str = "data") -> list[dict]:
    """Load all .txt documents from data directory."""
    data_path = Path(data_dir)
    documents = []

    for file_path in sorted(data_path.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8")
        documents.append({
            "filename": file_path.name,
            "content": content,
            "char_count": len(content),
            "line_count": len(content.splitlines()),
        })

    return documents
