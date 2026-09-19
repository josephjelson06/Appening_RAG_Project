"""Create structure-aware RAG chunks from the extracted text and tables."""

import ast
import json
import re
from pathlib import Path


TEXT_INPUT = Path("extracted_text_pages_7_58.txt")
TABLE_INPUT = Path("extracted_tables_7_58.txt")
OUTPUT = Path("chunked_documents.jsonl")

MAX_TEXT_CHARS = 2800
TEXT_OVERLAP_CHARS = 300
MAX_TABLE_CHARS = 4500

METADATA_RE = re.compile(
    r"PDF PAGE (\d+) \| IN-BOOK PAGE (\d+) \| "
    r"(Chapter \d+): (.*?) \| SECTION (.*?) \| TABLE (\d+)"
)


def parse_text_pages(path):
    raw = path.read_text(encoding="utf-8")
    records = []
    sections = re.split(r"\n={80}\n", raw)

    for index in range(0, len(sections) - 1, 2):
        header = sections[index]
        body = sections[index + 1]
        match = re.search(
            r"PDF page: (\d+) \| In-book page: (\d+) \| "
            r"(Chapter \d+): (.*?) \| Section: (.*)",
            header,
        )
        if not match:
            continue

        pdf_page, in_book_page, chapter, chapter_title, section_name = match.groups()
        records.append(
            {
                "text": body.strip(),
                "metadata": {
                    "source": "Ebook-Agentic-AI.pdf",
                    "content_type": "text",
                    "pdf_page": int(pdf_page),
                    "in_book_page": int(in_book_page),
                    "chapter": chapter,
                    "chapter_title": chapter_title.strip(),
                    "section": section_name.strip(),
                },
            }
        )

    return records


def parse_table_blocks(path):
    raw = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n={80}\n", raw)
    records = []

    for index in range(0, len(blocks) - 1, 2):
        header = blocks[index]
        rows_text = blocks[index + 1]
        match = METADATA_RE.search(header)
        if not match:
            continue

        pdf_page, in_book_page, chapter, chapter_title, section_name, table_number = match.groups()
        rows = []
        for line in rows_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = ast.literal_eval(line)
            except (SyntaxError, ValueError):
                continue
            if isinstance(row, list):
                rows.append(["" if value is None else str(value).strip() for value in row])

        if not rows:
            continue

        records.append(
            {
                "rows": rows,
                "metadata": {
                    "source": "Ebook-Agentic-AI.pdf",
                    "content_type": "table",
                    "pdf_page": int(pdf_page),
                    "in_book_page": int(in_book_page),
                    "chapter": chapter,
                    "chapter_title": chapter_title.strip(),
                    "section": section_name.strip(),
                    "table_number": int(table_number),
                },
            }
        )

    return records


def split_text(text, max_chars=MAX_TEXT_CHARS, overlap=TEXT_OVERLAP_CHARS):
    """Split on paragraphs, then sentences, then words as a final fallback."""
    if not text or not text.strip():
        return []

    if len(text) <= max_chars:
        return [text.strip()]

    chunks = []
    remaining = text.strip()
    separators = ["\n\n", "\n", ". ", " "]

    while len(remaining) > max_chars:
        cut = -1
        for separator in separators:
            candidate = remaining.rfind(separator, 0, max_chars)
            if candidate > max_chars // 2:
                cut = candidate + len(separator)
                break
        if cut == -1:
            cut = max_chars

        chunk = remaining[:cut].strip()
        if chunk:
            chunks.append(chunk)

        start = max(0, cut - overlap)
        remaining = remaining[start:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks


def table_to_text(rows):
    header = rows[0]
    lines = ["Table columns: " + " | ".join(header)]
    for row in rows[1:]:
        pairs = []
        for index, value in enumerate(row):
            column = header[index] if index < len(header) else f"Column {index + 1}"
            pairs.append(f"{column}: {value}")
        lines.append("; ".join(pairs))
    return "\n".join(lines)


def build_chunks():
    chunks = []

    for record in parse_text_pages(TEXT_INPUT):
        for part_number, text in enumerate(split_text(record["text"]), start=1):
            metadata = dict(record["metadata"])
            metadata.update({"chunk_type": "text", "part_number": part_number})
            chunks.append({"text": text, "metadata": metadata})

    for record in parse_table_blocks(TABLE_INPUT):
        table_text = table_to_text(record["rows"])
        parts = split_text(table_text, max_chars=MAX_TABLE_CHARS, overlap=0)
        for part_number, text in enumerate(parts, start=1):
            metadata = dict(record["metadata"])
            metadata.update({"chunk_type": "table", "part_number": part_number})
            chunks.append({"text": text, "metadata": metadata})

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        prefix = "table" if metadata["content_type"] == "table" else "text"
        chunk["id"] = (
            f"ebook-p{metadata['pdf_page']}-{prefix}-"
            f"{metadata['part_number']}-{index:04d}"
        )

    return chunks


if __name__ == "__main__":
    chunks = build_chunks()
    with OUTPUT.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Wrote {len(chunks)} chunks to {OUTPUT}")
