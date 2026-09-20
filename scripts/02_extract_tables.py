import sys
from pathlib import Path

import pymupdf  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_rag.ingestion.metadata import metadata_for_page, update_section


PDF_PATH = PROJECT_ROOT / "data" / "raw" / "Ebook-Agentic-AI.pdf"
OUTPUT_PATH = PROJECT_ROOT / "data" / "artifacts" / "02_cleaned" / "cleaned_tables_7_58.txt"

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


COLOR_LABELS = {
    (0, 116, 186): "Very High",  # blue
    (70, 184, 102): "High",       # green
    (252, 213, 61): "Moderate",  # yellow
    (221, 95, 64): "Initial",    # red
}


def nearest_color_label(fill):
    if not fill:
        return None

    rgb = tuple(round(channel * 255) for channel in fill[:3])
    distances = {
        label: sum((rgb[i] - color[i]) ** 2 for i in range(3))
        for color, label in COLOR_LABELS.items()
    }
    label, distance = min(distances.items(), key=lambda item: item[1])
    return label if distance < 5000 else None


def extract_table_data(page, table, page_number):
    """Extract cells and decode the colored readiness matrix on page 52."""
    data = table.extract()

    if page_number != 52 or len(data) != 6 or len(data[0]) != 7:
        return data

    row_count = len(data)
    color_markers = []
    for drawing in page.get_drawings():
        label = nearest_color_label(drawing.get("fill"))
        rect = drawing.get("rect")
        if label and rect and rect.width < 25 and rect.height < 25:
            color_markers.append((pymupdf.Rect(rect), label))

    for row_index in range(1, row_count):
        for column_index in range(1, len(data[row_index])):
            cell_index = column_index * row_count + row_index
            cell = pymupdf.Rect(table.cells[cell_index])
            center = cell.tl + (cell.br - cell.tl) * 0.5

            for marker_rect, label in color_markers:
                if marker_rect.contains(center):
                    data[row_index][column_index] = label
                    break

    return data


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
        data = extract_table_data(page, table, page_number)

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


output_lines = []

for table in table_pages:
    output_lines.extend(
        [
            "",
            "=" * 80,
            (
                f"PDF PAGE {table['page_number']} | "
                f"IN-BOOK PAGE {table['in_book_page']} | "
                f"{table['chapter']}: {table['chapter_title']} | "
                f"SECTION {table['section']} | "
                f"TABLE {table['table_number']}"
            ),
            "=" * 80,
        ]
    )

    output_lines.extend(str(row) for row in table["data"])


with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
    output_file.write("\n".join(output_lines).lstrip() + "\n")

print(f"Saved extracted tables to {OUTPUT_PATH}")

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
