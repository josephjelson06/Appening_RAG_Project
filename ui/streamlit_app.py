"""Streamlit client for the Agentic AI Book RAG API."""

import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:18000")

st.set_page_config(page_title="Agentic AI Book Assistant", layout="wide")
st.title("Agentic AI Book Assistant")
st.caption("Ask questions about the Agentic AI for Executives book.")

with st.sidebar:
    st.header("Connection")
    api_url = st.text_input("FastAPI base URL", value=DEFAULT_API_URL).rstrip("/")
    st.markdown("The UI calls the FastAPI `/retrieve` and `/generate` routes.")


def call_api(route, question):
    try:
        response = requests.post(
            f"{api_url}{route}", json={"question": question}, timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None


def show_source(metadata, score=None):
    label = (
        f"PDF page {metadata.get('pdf_page', '?')} | "
        f"in-book page {metadata.get('in_book_page', '?')}"
    )
    for key in ("chapter", "section", "content_type"):
        if metadata.get(key):
            label += f" | {metadata[key]}"
    if metadata.get("table_number"):
        label += f" | table {metadata['table_number']}"
    if score is not None:
        label += f" | score {score:.3f}"
    st.caption(label)


question = st.text_area(
    "Question",
    placeholder="For example: What are the capabilities of Agentic AI?",
    height=100,
)

retrieve_tab, generate_tab = st.tabs(["Retrieve context", "Generate answer"])

with retrieve_tab:
    if st.button("Retrieve", type="secondary", disabled=not question.strip()):
        result = call_api("/retrieve", question.strip())
        if result is not None:
            st.write(f"Retrieved {result['match_count']} matching chunks.")
            for match in result["matches"]:
                with st.expander(match["id"]):
                    show_source(match["metadata"], match["score"])
                    st.write(match["text"])

with generate_tab:
    if st.button("Generate answer", type="primary", disabled=not question.strip()):
        result = call_api("/generate", question.strip())
        if result is not None:
            st.subheader("Answer")
            st.write(result["answer"])
            st.subheader("Sources")
            for source in result["sources"]:
                show_source(source["metadata"], source["score"])
