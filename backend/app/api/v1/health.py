from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "short_name": settings.APP_SHORT_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "ocr_engine": settings.OCR_ENGINE,
        "language": settings.OCR_LANGUAGE,
        "use_gpu": settings.OCR_USE_GPU,
    }
