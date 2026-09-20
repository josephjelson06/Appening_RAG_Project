import sys
from pathlib import Path

import pymupdf  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_rag.config import PATHS
from agentic_rag.ingestion.metadata import metadata_for_page, update_section
from agentic_rag.ingestion.cleaner import clean_text


PDF_PATH = PATHS.source_pdf
OUTPUT_PATH = PATHS.cleaned_dir / "cleaned_text_pages_7_58.txt"

START_PAGE = 7
END_PAGE = 58
IGNORED_PAGES = {28, 49}


def is_non_educational_block(text, page_number):
    """Remove recurring layout and explicitly promotional/QR content."""
    normalized = " ".join(text.split())

    # Repeated book branding and the in-book footer number.
    if normalized == "AGENTIC AI FOR EXECUTIVES":
        return True
    if normalized == str(page_number - 6):
        return True

    # QR-code calls to action are promotional references, not educational text.
    if "QR code" in normalized or "Scan the QR" in normalized:
        return True

    # The Emergence AI material on PDF page 46 is a promotional insert. The
    # caller handles the remainder of that page after its heading separately.
    if page_number == 46 and (
        "Emergence AI" in normalized
        or normalized.startswith("Leaders in Autonomous Multi-Agent")
    ):
        return True

    return False


def cell_text(cell):
    if cell is None:
        return ""
    return str(cell).strip()


def is_real_table(data):
    """Use the same content checks as Find_Table.py."""
    if not data:
        return False

    populated_rows = []
    for row in data:
        populated_cells = [cell_text(cell) for cell in row]
        populated_cells = [cell for cell in populated_cells if cell]
        if populated_cells:
            populated_rows.append(populated_cells)

    if len(populated_rows) < 2:
        return False

    max_populated_cells_in_row = max(len(row) for row in populated_rows)
    if max_populated_cells_in_row < 2:
        return False

    longest_cell = max(len(cell) for row in populated_rows for cell in row)
    if len(populated_rows) <= 2 and longest_cell > 200:
        return False

    return True


def get_real_table_rects(page):
    """Return bounding boxes only for tables that passed our validator."""
    table_rects = []

    for table in page.find_tables().tables:
        if is_real_table(table.extract()):
            table_rects.append(pymupdf.Rect(table.bbox))

    return table_rects


def block_is_inside_table(block, table_rects):
    """Determine whether a text block belongs to an accepted table."""
    block_rect = pymupdf.Rect(block[:4])
    if block_rect.is_empty:
        return False

    block_area = block_rect.get_area()

    for table_rect in table_rects:
        intersection = block_rect & table_rect
        if intersection.is_empty:
            continue

        # Table text blocks are normally entirely inside the table rectangle.
        # The overlap ratio also handles blocks that slightly cross a border.
        overlap_ratio = intersection.get_area() / block_area
        if table_rect.contains(block_rect) or overlap_ratio >= 0.50:
            return True

    return False


def extract_page_text(page):
    table_rects = get_real_table_rects(page)
    text_blocks = page.get_text("blocks", sort=True)

    text_parts = []
    skip_remaining_promotional_content = False
    for block in text_blocks:
        if block_is_inside_table(block, table_rects):
            continue

        text = block[4].strip()
        if not text:
            continue

        normalized = " ".join(text.split())
        if page.number == 45 and normalized.startswith(
            "Leaders in Autonomous Multi-Agent"
        ):
            skip_remaining_promotional_content = True

        if skip_remaining_promotional_content:
            continue

        if not is_non_educational_block(text, page.number + 1):
            text_parts.append(text)

    return "\n\n".join(text_parts)


doc = pymupdf.open(PDF_PATH)
page_outputs = []
current_section = None

for page_number in range(START_PAGE, END_PAGE + 1):
    if page_number in IGNORED_PAGES:
        continue

    page = doc[page_number - 1]
    if page_number in {START_PAGE, 18, 29, 39, 48, 54}:
        current_section = None
    text = extract_page_text(page)
    text = clean_text(text, page_number)
    current_section = update_section(current_section, text)
    metadata = metadata_for_page(page_number, current_section)

    page_outputs.append(
        f"{'=' * 80}\n"
        f"PDF page: {metadata['pdf_page']} | "
        f"In-book page: {metadata['in_book_page']} | "
        f"{metadata['chapter']}: {metadata['chapter_title']} | "
        f"Section: {metadata['section']}\n"
        f"{'=' * 80}\n{text}"
    )


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
    output_file.write("\n\n".join(page_outputs))


print(f"Saved text from pages {START_PAGE}-{END_PAGE} to {OUTPUT_PATH}")
print(f"Ignored pages: {sorted(IGNORED_PAGES)}")
