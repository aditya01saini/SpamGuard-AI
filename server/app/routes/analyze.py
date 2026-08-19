"""Routes: /api/analyze and /api/analyze/upload."""

from __future__ import annotations

from fastapi import APIRouter, File, Request, UploadFile

from app.config import settings
from app.controllers import analysis_controller
from app.schemas.requests import AnalyzeRequest
from app.services import email_parser
from app.utils.exceptions import FileTooLargeError, InvalidFileError
from app.utils.response import ok

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """Analyze a pasted email (subject + body)."""
    parsed = email_parser.parse_email_text(req.subject, req.body, req.sender)
    result = await analysis_controller.analyze_email(parsed)
    return ok(result)


@router.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Analyze an uploaded .txt or .eml email."""
    content = await file.read()

    # 1. Size validation.
    if len(content) == 0:
        raise InvalidFileError("Uploaded file is empty.")
    if len(content) > settings.max_file_size_bytes:
        raise FileTooLargeError(
            f"File exceeds the maximum allowed size of {settings.max_file_size_mb} MB."
        )

    # 2. Extension + MIME validation (done inside the parser for extensions).
    filename = file.filename or "email.txt"
    email_parser.validate_filename(filename)

    # 3. Safe parsing (no execution of attachments/scripts).
    parsed = email_parser.parse_email_bytes(content, filename)
    result = await analysis_controller.analyze_email(parsed)
    return ok(result)
