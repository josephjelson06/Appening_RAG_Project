import re


CHAPTERS = (
    (7, 17, "Chapter 1", "Introduction to Agentic AI"),
    (18, 28, "Chapter 2", "Agentic AI Systems"),
    (29, 38, "Chapter 3", "Multi-Agent Systems"),
    (39, 47, "Chapter 4", "Orchestrating Multi-Agent Systems"),
    (48, 53, "Chapter 5", "Organizational Maturity and Readiness"),
    (54, 58, "Chapter 6", "Practical Applications of Agentic AI"),
)


def chapter_for_page(page_number):
    for first_page, last_page, number, title in CHAPTERS:
        if first_page <= page_number <= last_page:
            return number, title
    return "Unknown chapter", "Unknown chapter"


def in_book_page(page_number):
    return page_number - 6


def update_section(current_section, page_text):
    """Return the latest numbered section found in this page's text."""
    section = current_section

    for line in page_text.splitlines():
        line = " ".join(line.split())
        match = re.match(r"^(\d+\.\d+)\s+(.+?)\s*$", line)
        if match:
            section = f"{match.group(1)} {match.group(2)}"

        # Chapter 5 uses lettered sections such as "B. Industry-Wise
        # Readiness" instead of numeric section labels.
        letter_match = re.match(r"^([A-Z])\.\s+(.+?)\s*$", line)
        if letter_match:
            section = f"{letter_match.group(1)}. {letter_match.group(2)}"

    return section or "Chapter introduction"


def metadata_for_page(page_number, section):
    chapter_number, chapter_title = chapter_for_page(page_number)
    return {
        "pdf_page": page_number,
        "in_book_page": in_book_page(page_number),
        "chapter": chapter_number,
        "chapter_title": chapter_title,
        "section": section or "Chapter introduction",
    }
