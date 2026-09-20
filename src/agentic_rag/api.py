"""FastAPI interface for retrieval and grounded generation."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .ask import answer
from .retrieve import retrieve


app = FastAPI(
    title="Agentic AI Book RAG API",
    description="Retrieve and answer questions from the Agentic AI book.",
    version="0.1.0",
)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Question about the book")


class RetrievedChunk(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict


class RetrievalResponse(BaseModel):
    question: str
    matches: list[RetrievedChunk]
    match_count: int


class SourceReference(BaseModel):
    id: str
    score: float
    metadata: dict


class GenerationResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceReference]
    grounded: bool
    validation_note: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/retrieve", response_model=RetrievalResponse)
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


@app.post("/generate", response_model=GenerationResponse)
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
