import pymupdf  # PyMuPDF
from document_metadata import metadata_for_page, update_section


PDF_PATH = "Ebook-Agentic-AI.pdf"

# Keep both extraction pipelines on the same in-book content range.
START_PAGE = 7
END_PAGE = 58
IGNORED_PAGES = {28, 49}


def cell_text(cell):
    """Return a normalized cell value, treating None and whitespace as empty."""
    if cell is None:
        return ""
    return str(cell).strip()


def is_real_table(data):
    """Reject layout boxes and prose blocks returned as tables."""
    if not data:
        return False

    populated_rows = []
    for row in data:
        populated_cells = [cell_text(cell) for cell in row]
        populated_cells = [cell for cell in populated_cells if cell]
        if populated_cells:
            populated_rows.append(populated_cells)

    # Ignore empty grid fragments and one-cell decorative objects.
    if len(populated_rows) < 2:
        return False

    max_populated_cells_in_row = max(len(row) for row in populated_rows)
    if max_populated_cells_in_row < 2:
        return False

    # A title plus a long paragraph is not a table. Real two-row tables with
    # short cells are still allowed through this rule.
    longest_cell = max(len(cell) for row in populated_rows for cell in row)
    if len(populated_rows) <= 2 and longest_cell > 200:
        return False

    return True


doc = pymupdf.open(PDF_PATH)
table_pages = []
current_section = None

for page_number, page in enumerate(doc, start=1):
    if not START_PAGE <= page_number <= END_PAGE:
        continue
    if page_number in IGNORED_PAGES:
        continue

    if page_number in {7, 18, 29, 39, 48}:
        current_section = None

    tables = page.find_tables()
    page_text = page.get_text("text")
    current_section = update_section(current_section, page_text)
    metadata = metadata_for_page(page_number, current_section)
    accepted_table_number = 0

    for table in tables.tables:
        data = table.extract()

        if not is_real_table(data):
            continue

        accepted_table_number += 1

        # A page can contain more than one section. Use the latest heading
        # physically above this table, rather than the final heading on the
        # whole page.
        table_section = current_section
        table_top = table.bbox[1]
        for block in page.get_text("blocks", sort=True):
            if block[3] <= table_top:
                table_section = update_section(table_section, block[4])

        table_metadata = metadata_for_page(page_number, table_section)

        table_pages.append(
            {
                "page_number": page_number,
                "in_book_page": table_metadata["in_book_page"],
                "chapter": table_metadata["chapter"],
                "chapter_title": table_metadata["chapter_title"],
                "section": table_metadata["section"],
                "table_number": accepted_table_number,
                "data": data,
            }
        )


for table in table_pages:
    print("\n" + "=" * 80)
    print(
        f"PDF PAGE {table['page_number']} | "
        f"IN-BOOK PAGE {table['in_book_page']} | "
        f"{table['chapter']}: {table['chapter_title']} | "
        f"SECTION {table['section']} | "
        f"TABLE {table['table_number']}"
    )
    print("=" * 80)

    for row in table["data"]:
        print(row)
