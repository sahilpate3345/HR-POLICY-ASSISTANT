from pathlib import Path
from typing import List
from hr_assistant.config import DATA_FILE_PATH


class SimpleDocument:
    """Document wrapper storing page content and metadata."""
    def __init__(self, page_content: str, metadata: dict = None, id: str = None):
        self.page_content = page_content
        self.metadata = metadata or {}
        self.id = id

    def __repr__(self):
        source = self.metadata.get("source", "unknown")
        return f"<Document source='{source}' length={len(self.page_content)}>"


def load_document(file_path: str | Path = DATA_FILE_PATH) -> List[SimpleDocument]:
    """Dynamically loads text or markdown document from file_path."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    doc = SimpleDocument(
        page_content=content,
        metadata={"source": str(file_path), "file_name": file_path.name}
    )
    return [doc]