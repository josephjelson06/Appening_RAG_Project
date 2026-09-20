# Preprocessing and Cleaning Decisions

This document explains why parts of the source PDF were included, excluded,
or transformed before indexing.

## Page range

The useful educational content is extracted from PDF pages 7–58. PDF pages 1–6
are front matter and PDF pages 59–60 are outside the selected book-content
range, so they are not included.

PDF pages 28 and 49 are also excluded explicitly.

- **PDF page 28:** excluded as part of the known extraction exclusions.
- **PDF page 49:** contains a flowchart whose visual relationships are not
  reliably represented by ordinary text/table extraction. It is the one
  knowledge-bearing page intentionally left out rather than indexed as
  misleading text.

## Promotional and layout content

The following content is removed from the page-text knowledge base:

- repeated `AGENTIC AI FOR EXECUTIVES` headers;
- footer page numbers;
- QR-code calls to action and “For more case studies” promotional text;
- the Emergence AI promotional insert on PDF page 46;
- other known promotional blocks identified in the source-specific cleaner.

These elements do not explain Agentic AI concepts from the book and would add
noise to retrieval. Removing them also prevents the same header or promotion
from appearing in many unrelated answers.

The cleaner preserves educational paragraphs, headings, lists, and section
content. It does not flatten the page text into a single summary; paragraph
boundaries remain available to the chunking stage.

## Separate page and table extraction

Page extraction identifies accepted table rectangles and removes their text
blocks from the page-text stream. Table extraction independently validates and
serializes real tables. This separation prevents duplicate evidence: table
content is indexed as a table chunk, not once as a page paragraph and again as
a table.

The table validator rejects empty grid fragments, one-cell decorative objects,
and prose blocks that a PDF parser incorrectly reports as tables.

## Color-coded table on PDF page 52

The organizational readiness matrix uses colored circles instead of words for
readiness levels. The extractor reads the legend and writes the semantic labels
into the table data:

| Color | Stored text label |
| --- | --- |
| Blue | Very High |
| Green | High |
| Yellow | Moderate |
| Red | Initial |

This makes the table searchable and allows questions about readiness levels to
be answered from text embeddings without requiring the model to see the image.
