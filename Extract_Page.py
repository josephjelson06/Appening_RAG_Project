import pymupdf  # PyMuPDF
from document_metadata import metadata_for_page, update_section


PDF_PATH = "Ebook-Agentic-AI.pdf"
OUTPUT_PATH = "extracted_text_pages_7_58.txt"

START_PAGE = 7
END_PAGE = 58
IGNORED_PAGES = {28, 49}


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
    for block in text_blocks:
        if block_is_inside_table(block, table_rects):
            continue

        text = block[4].strip()
        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)


doc = pymupdf.open(PDF_PATH)
page_outputs = []
current_section = None

for page_number in range(START_PAGE, END_PAGE + 1):
    if page_number in IGNORED_PAGES:
        continue

    page = doc[page_number - 1]
    if page_number in {START_PAGE, 18, 29, 39, 48}:
        current_section = None
    text = extract_page_text(page)
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


with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
    output_file.write("\n\n".join(page_outputs))


print(f"Saved text from pages {START_PAGE}-{END_PAGE} to {OUTPUT_PATH}")
print(f"Ignored pages: {sorted(IGNORED_PAGES)}")
