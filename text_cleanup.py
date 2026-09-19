"""Text cleanup rules for the designed source PDF."""

import re


def clean_text(text: str, pdf_page: int) -> str:
    """Remove headers, logos, QR promotions, and page-specific artifacts."""
    text = text.replace("\ufffd", " ")

    patterns = [
        r"AGENTIC\s+AI\s+FOR\s+EXECUTIVES",
        r"Konverg(?:e|&#x65;)\s*\.??\s*AI",
        r"For\s+more\s+case\s+studies\s+scan\s+the\s+QR\s+code",
        r"Know\s+your\s+Stage\s*\?\s*Scan\s+the\s+QR\s*(?:and\s+know\s+your\s+organization'?s\s+readiness)?",
        r"Leaders\s+in\s+Autonomous\s+Multi-Agent\s+Orchestration\s+for\s+Enterprise.*?Scan\s+the\s+QR\s+code\s+to\s+learn\s+more\s+about\s+Emergence\s+AI",
        r"Emergence\s+AI\s+is\s+collaborating\s+with.*",
        r"For\s+more\s+case\s+studies\s+scan\s+the",
        r"Scan\s+the\s+QR\s+code(?:\s+to\s+learn\s+more)?",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    # The designed layout places this heading at the end of the preceding
    # extracted text block, so support both physical pages.
    if pdf_page in {57, 58}:
        text = re.sub(
            r"AI-Powered\s+Loan\s+Eligibility\s+Automation",
            "",
            text,
            flags=re.IGNORECASE,
        )

    # The footer is the in-book page number, which is PDF page minus six.
    in_book_page = pdf_page - 6
    text = re.sub(rf"(?:\s|^)\s*{in_book_page}\s*$", "", text)

    return re.sub(r"\s+", " ", text).strip()
