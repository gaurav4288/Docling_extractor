from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
from io import BytesIO
import logging


logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def health():
    """Health check endpoint for load balancers / probes"""
    return {"status": "ok"}


import os
import tempfile
import asyncio
from uuid import uuid4
from app.core.config import settings

# Use a cross-platform temp directory. Prefer $TEMP_DIR env var, then configured UPLOAD_DIR, then system temp.
TEMP_DIR = Path(
    os.environ.get("TEMP_DIR", settings.UPLOAD_DIR or tempfile.gettempdir())
)
TEMP_DIR = Path(TEMP_DIR)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/convert")
async def convert(
    file: UploadFile = File(...),
    service: str = "marker",
):
    """Convert an uploaded file using the selected backend service.

    service: one of ['marker', 'pdfplumber', 'docling']
    """
    # Save uploaded file to disk
    from app.services.marker import MarkerProcessor
    from app.services.pdfplumber import FormProcessor
    from app.services.docling import DoclingService

    # Sanitize filename and add unique prefix to avoid collisions and directory traversal
    safe_name = Path(file.filename).name
    input_path = TEMP_DIR / f"{uuid4().hex}_{safe_name}"
    with input_path.open("wb") as buffer:
        buffer.write(await file.read())

    try:
        if service == "marker":
            processor = MarkerProcessor()
            # Processor is CPU / IO bound — run in a thread to avoid blocking the event loop
            markdown = await asyncio.to_thread(processor.process_file, input_path)

        elif service == "pdfplumber":
            processor = FormProcessor()
            markdown = await asyncio.to_thread(processor.process_file, input_path)
        elif service == "docling":
            processor = DoclingService()
            result = await asyncio.to_thread(processor.process_file, input_path)
            if isinstance(result, dict) and "markdown" in result:
                markdown = result["markdown"]
            else:
                markdown = result
        else:
            raise HTTPException(
                status_code=400,
                detail="Unknown service. Choose marker, pdfplumber, or docling",
            )

    except Exception as e:
        logger.exception("Conversion failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file even if conversion fails
        if input_path.exists():
            input_path.unlink()

    # Stream Response
    md_file = BytesIO(str(markdown).encode("utf-8"))
    return StreamingResponse(
        md_file,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={file.filename}.md"},
    )
