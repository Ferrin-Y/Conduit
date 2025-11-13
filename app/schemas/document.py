from pydantic import BaseModel, ConfigDict, Field

from app.models import DocumentStatus


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: DocumentStatus


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class QueryResult(BaseModel):
    text: str
    distance: float
    document_id: int | None


class QueryResponse(BaseModel):
    results: list[QueryResult]
