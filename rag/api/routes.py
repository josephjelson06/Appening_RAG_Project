"""HTTP routes for retrieval and grounded generation."""

from fastapi import APIRouter, HTTPException

from ..generation.generator import answer
from ..retrieval.retriever import retrieve
from .schemas import (
    GenerationResponse,
    QueryRequest,
    RetrievalResponse,
)


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_route(request: QueryRequest):
    try:
        matches = retrieve(request.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Retrieval failed: {exc}") from exc

    return {
        "question": request.question,
        "matches": matches,
        "match_count": len(matches),
    }


@router.post("/generate", response_model=GenerationResponse)
def generate_route(request: QueryRequest):
    try:
        result = answer(request.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Generation failed: {exc}") from exc

    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "grounded": result["grounded"],
        "validation_note": result["validation_note"],
    }
