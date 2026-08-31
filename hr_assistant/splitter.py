import re
from typing import List, Any
from hr_assistant.config import CHUNK_SIZE, CHUNK_OVERLAP
from hr_assistant.document_loader import SimpleDocument


def split_into_chunks(documents: List[Any], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[SimpleDocument]:
    """Dynamically splits documents into chunks while preserving section headings."""
    chunks = []
    header_pattern = re.compile(r"^(?:\d+\.\s*|[#]{1,4}\s*)([A-Z0-9\s\-_]+)$")

    for doc in documents:
        lines = doc.page_content.split("\n")
        current_header = "GENERAL POLICY"
        current_lines = []

        sections = []
        for line in lines:
            line_str = line.strip()
            if header_pattern.match(line_str) and len(line_str) < 60:
                if current_lines:
                    sections.append((current_header, "\n".join(current_lines).strip()))
                    current_lines = []
                current_header = line_str
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_header, "\n".join(current_lines).strip()))

        chunk_id = 0
        for header, sec_text in sections:
            if not sec_text:
                continue
            paras = sec_text.split("\n\n")
            curr_chunk = []
            curr_len = 0
            
            for para in paras:
                para = para.strip()
                if not para:
                    continue
                if curr_len + len(para) <= chunk_size:
                    curr_chunk.append(para)
                    curr_len += len(para) + 2
                else:
                    if curr_chunk:
                        chunk_text = f"[{header}]\n" + "\n\n".join(curr_chunk)
                        meta = dict(doc.metadata)
                        meta.update({"section": header, "chunk_id": chunk_id})
                        chunks.append(SimpleDocument(page_content=chunk_text, metadata=meta))
                        chunk_id += 1
                    curr_chunk = [para]
                    curr_len = len(para)

            if curr_chunk:
                chunk_text = f"[{header}]\n" + "\n\n".join(curr_chunk)
                meta = dict(doc.metadata)
                meta.update({"section": header, "chunk_id": chunk_id})
                chunks.append(SimpleDocument(page_content=chunk_text, metadata=meta))
                chunk_id += 1

    return chunks
