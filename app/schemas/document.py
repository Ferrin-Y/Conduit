from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import DocumentStatus


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    source_url: str | None = None

    @model_validator(mode="after")
    def require_content_or_url(self):
        if not self.content and not self.source_url:
            raise ValueError("either content or source_url is required")
        if self.content and self.source_url:
            raise ValueError("provide content or source_url, not both")
        return self


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
