"""Request and response schemas for the RAG API."""

from pydantic import BaseModel, Field


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
