"""Extract cleaned page text and structured tables from the source PDF.

The two public functions are intentionally separate:

* ``extract_pages`` extracts educational page text while excluding accepted
  table regions and promotional layout blocks.
* ``extract_tables`` extracts only validated tables and preserves table
  provenance. It also converts the color-coded readiness matrix on PDF page
  52 into readable labels.
"""

from pathlib import Path

import pymupdf

from ..config import PATHS
from .cleaner import clean_text
from .metadata import metadata_for_page, update_section


START_PAGE = 7
END_PAGE = 58
IGNORED_PAGES = {28, 49}
CHAPTER_STARTS = {7, 18, 29, 39, 48, 54}

TEXT_OUTPUT = PATHS.cleaned_dir / "cleaned_text_pages_7_58.txt"
TABLE_OUTPUT = PATHS.cleaned_dir / "cleaned_tables_7_58.txt"

COLOR_LABELS = {
    (0, 116, 186): "Very High",
    (70, 184, 102): "High",
    (252, 213, 61): "Moderate",
    (221, 95, 64): "Initial",
}


def cell_text(cell) -> str:
    """Return a normalized table-cell value."""
    return "" if cell is None else str(cell).strip()


def is_real_table(data) -> bool:
    """Reject layout boxes and prose blocks returned as tables."""
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


def is_non_educational_block(text: str, page_number: int) -> bool:
    """Identify repeated branding, footers, QR prompts, and promotions."""
    normalized = " ".join(text.split())

    if normalized == "AGENTIC AI FOR EXECUTIVES":
        return True
    if normalized == str(page_number - 6):
        return True
    if "QR code" in normalized or "Scan the QR" in normalized:
        return True
    if page_number == 46 and (
        "Emergence AI" in normalized
        or normalized.startswith("Leaders in Autonomous Multi-Agent")
    ):
        return True

    return False


def get_real_table_rects(page) -> list[pymupdf.Rect]:
    """Return bounding boxes only for tables accepted by the validator."""
    return [
        pymupdf.Rect(table.bbox)
        for table in page.find_tables().tables
        if is_real_table(table.extract())
    ]


def block_is_inside_table(block, table_rects: list[pymupdf.Rect]) -> bool:
    """Return whether a text block belongs to an accepted table."""
    block_rect = pymupdf.Rect(block[:4])
    if block_rect.is_empty:
        return False

    block_area = block_rect.get_area()
    for table_rect in table_rects:
        intersection = block_rect & table_rect
        if intersection.is_empty:
            continue

        overlap_ratio = intersection.get_area() / block_area
        if table_rect.contains(block_rect) or overlap_ratio >= 0.50:
            return True

    return False


def extract_page_text(page) -> str:
    """Extract non-table educational text from one PDF page."""
    table_rects = get_real_table_rects(page)
    text_parts = []
    skip_remaining_promotional_content = False

    for block in page.get_text("blocks", sort=True):
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


def extract_pages(
    pdf_path: Path = PATHS.source_pdf,
    output_path: Path = TEXT_OUTPUT,
) -> Path:
    """Extract and write cleaned educational text from the selected pages."""
    page_outputs = []
    current_section = None

    with pymupdf.open(pdf_path) as document:
        for page_number in range(START_PAGE, END_PAGE + 1):
            if page_number in IGNORED_PAGES:
                continue

            page = document[page_number - 1]
            if page_number in CHAPTER_STARTS:
                current_section = None

            text = clean_text(extract_page_text(page), page_number)
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(page_outputs), encoding="utf-8")
    print(f"Saved text from pages {START_PAGE}-{END_PAGE} to {output_path}")
    print(f"Ignored pages: {sorted(IGNORED_PAGES)}")
    return output_path


def nearest_color_label(fill) -> str | None:
    """Map a PDF drawing fill color to a readiness-stage label."""
    if not fill:
        return None

    rgb = tuple(round(channel * 255) for channel in fill[:3])
    distances = {
        label: sum((rgb[i] - color[i]) ** 2 for i in range(3))
        for color, label in COLOR_LABELS.items()
    }
    label, distance = min(distances.items(), key=lambda item: item[1])
    return label if distance < 5000 else None


def extract_table_data(page, table, page_number: int):
    """Extract a table, decoding the color-coded matrix on PDF page 52."""
    data = table.extract()

    if page_number != 52 or len(data) != 6 or len(data[0]) != 7:
        return data

    color_markers = []
    for drawing in page.get_drawings():
        label = nearest_color_label(drawing.get("fill"))
        rect = drawing.get("rect")
        if label and rect and rect.width < 25 and rect.height < 25:
            color_markers.append((pymupdf.Rect(rect), label))

    row_count = len(data)
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


def extract_tables(
    pdf_path: Path = PATHS.source_pdf,
    output_path: Path = TABLE_OUTPUT,
) -> Path:
    """Extract validated tables and write them with complete provenance."""
    table_pages = []
    current_section = None

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            if not START_PAGE <= page_number <= END_PAGE:
                continue
            if page_number in IGNORED_PAGES:
                continue

            if page_number in CHAPTER_STARTS:
                current_section = None

            current_section = update_section(current_section, page.get_text("text"))
            accepted_table_number = 0

            for table in page.find_tables().tables:
                data = extract_table_data(page, table, page_number)
                if not is_real_table(data):
                    continue

                accepted_table_number += 1
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines).lstrip() + "\n", encoding="utf-8")
    print(f"Saved extracted tables to {output_path}")
    return output_path

