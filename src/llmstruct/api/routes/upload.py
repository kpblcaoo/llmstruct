import uuid
import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from ..models import UploadResponse
from ..deps import get_api_key
import zipfile

UPLOAD_ROOT = Path(tempfile.gettempdir()) / "llmstruct_sessions"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_project(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """Загрузка архива проекта. Возвращает session_id."""
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    try:
        archive_path = session_dir / file.filename
        with archive_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        # Распаковываем архив
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(session_dir)
        archive_path.unlink()  # удаляем архив после распаковки
    except Exception as e:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(400, f"Ошибка при обработке архива: {e}")
    return UploadResponse(session_id=session_id) 