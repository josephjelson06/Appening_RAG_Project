# Prompt and Question Catalog

Use these prompts to understand what this application can answer and how it
behaves when a request is outside the ebook.

The expected behavior for an unsupported request is a grounded refusal such as
“I could not find sufficiently relevant information in the book.” The system
should not use outside knowledge or switch into a general-purpose writing mode.

## Correct page-text questions

Start with simple questions, then increase the difficulty:

1. **Direct definition:** What is Agentic AI?
2. **Section comparison:** How does Agentic AI differ from other AI systems?
3. **Section enumeration:** What are the capabilities of Agentic AI?
4. **Chapter-level synthesis:** What are the core pillars of an Agentic AI system,
   and how do they support autonomous behavior?
5. **Cross-section synthesis:** How do perception, reasoning, planning, learning,
   verification, and execution work together according to the book?
6. **Provenance request:** Which chapter and in-book page discuss the defining
   characteristics of an agent?

These questions primarily test page-text extraction, section metadata, chunking,
retrieval, and source references.

## Correct table questions

These questions test table extraction and table metadata:

1. What are the types of atomic agents listed in the table on PDF page 25?
2. Which industries are listed in the Agentic AI applications table?
3. What are the challenges and mitigation strategies shown in the multi-agent
   systems table?
4. In the organizational readiness table, what is the overall stage for
   Financial Services?
5. In the readiness matrix on PDF page 52, what is Healthcare’s Regulatory
   Adaptability level?
6. Which industry has “Very High” overall readiness in the color-coded matrix,
   and what do the colors mean?
7. What recommended strategy is associated with Level 3: Developing in the
   readiness-level table on PDF page 52?

For the color-coded matrix, the application converts the visual legend into
text labels: blue = Very High, green = High, yellow = Moderate, and red =
Initial.

## Unsupported or deliberately wrong prompts

These should not be answered using outside knowledge:

1. **Unrelated current fact:** Who is the prime minister of India?
2. **Fictional universe:** Who is Tony Stark, and what happens in Marvel films?
3. **Creative writing:** Write me a poem about the ocean.
4. **General programming request:** Write a Python web scraper for me.
5. **External recommendation:** Which embedding model should I use for my next
   project?
6. **Mixed request:** Explain Agentic AI from the ebook, then add three facts
   about it from sources outside the book.
7. **Omitted visual content:** Recreate the flowchart from PDF page 49 exactly.

The last prompt is intentionally unsupported by this dataset because PDF page
49 was excluded from ingestion. The assistant should explain that the requested
content is not available rather than inventing the flowchart.

## What to inspect while testing

For every request, compare:

- the answer;
- the retrieved chunks;
- PDF page and in-book page metadata;
- chapter, section, and content type;
- table number when the source is a table;
- the Pinecone similarity score.

The score is retrieval similarity, not a guarantee that the final answer is
correct. Unsupported prompts are especially useful for checking whether the
grounding instruction is being followed.
