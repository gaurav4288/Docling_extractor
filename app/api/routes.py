import shutil
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, HTTPException, File, BackgroundTasks
from fastapi.responses import Response
from app.core.config import settings
from app.services.processing import processor

router = APIRouter()

def cleanup_file(path: str):
    """Background task to remove temp file after response is sent."""
    try:
        os.remove(path)
    except Exception:
        pass

@router.post("/convert", summary="Convert PDF/Docx to clean Markdown")
async def convert_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # 1. Validation
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # 2. Save Upload Temporarily
    temp_file_path = Path(settings.UPLOAD_DIR) / file.filename
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save uploaded file.")

    # 3. Process with Docling (Blocking call wrapped in try/except)
    try:
        # Note: Docling is CPU intensive. In a massive scale app, 
        # you might run this in a Celery worker. For a service, this is fine.
        clean_text = processor.process_file(temp_file_path)
        
        # 4. Prepare Output Filename
        output_filename = f"{Path(file.filename).stem}_processed.md"

        # 5. Queue Cleanup
        background_tasks.add_task(cleanup_file, str(temp_file_path))

        # 6. Return as downloadable file
        return Response(
            content=clean_text,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )

    except Exception as e:
        # Ensure cleanup happens even on error
        cleanup_file(str(temp_file_path))
        raise HTTPException(status_code=500, detail=str(e))