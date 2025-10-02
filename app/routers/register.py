from fastapi import APIRouter, UploadFile, File
from uuid import uuid4

router = APIRouter(prefix="/register", tags=["register"])

@router.post("", summary="Register a source drawing file (PDF/Image)")
async def register_file(file: UploadFile = File(...)):
    # We only read size for metadata; content is not persisted in this stub.
    content = await file.read()
    file_id = str(uuid4())
    return {
        "ok": True,
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
    }
