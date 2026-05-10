import re
from collections.abc import Iterable
from clinical_rag_agent.schemas.rag import DocumentChunk, DocumentInput


def split_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs or [text.strip()]:
        if len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
        else:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            current = ""
            for sentence in sentences:
                if len(current) + len(sentence) + 1 <= max_chars:
                    current = f"{current} {sentence}".strip()
                else:
                    if current:
                        chunks.append(current)
                    current = sentence[:max_chars]
    if current:
        chunks.append(current)
    return chunks


def chunk_documents(documents: Iterable[DocumentInput]) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for doc_index, document in enumerate(documents):
        for chunk_index, text in enumerate(split_text(document.text)):
            safe_source = re.sub(r"[^a-zA-Z0-9_-]+", "_", document.source.lower()).strip("_") or "source"
            chunk_id = f"{safe_source}_{doc_index}_{chunk_index}"
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    source=document.source,
                    title=document.title,
                    text=text,
                    metadata=document.metadata,
                )
            )
    return chunks

