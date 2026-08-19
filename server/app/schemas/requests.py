"""Pydantic request schemas (input validation)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    subject: str = Field(default="", max_length=2000)
    sender: str = Field(default="", max_length=1000)
    body: str = Field(default="", max_length=100_000)


class AnalyzeUploadRequest(BaseModel):
    """Metadata for a file upload (the file itself comes via multipart)."""
    pass


class DeleteResponse(BaseModel):
    deleted: bool
    id: str
