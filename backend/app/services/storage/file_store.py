import json
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image

from app.core.config import settings
from app.schemas.document import DocumentResult


class FileStorageService:
    """
    Manages physical storage for documents, page renders, thumbnails, and JSON manifests.
    """

    MAGIC_BYTES = {
        b"%PDF": "application/pdf",
        b"\x89PNG\r\n\x1a\n": "image/png",
        b"\xff\xd8\xff": "image/jpeg",
        b"RIFF": "image/webp",
    }

    @classmethod
    def validate_file(cls, content: bytes, original_filename: str) -> tuple[bool, str, str]:
        """
        Validates extension, size, and magic bytes.
        Returns: (is_valid, mime_type, error_message)
        """
        # 1. Size check
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            return False, "", f"File size ({size_mb:.1f} MB) exceeds maximum limit of {settings.MAX_FILE_SIZE_MB} MB."

        # 2. Extension check
        ext = Path(original_filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False, "", f"File extension '{ext}' is not supported. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"

        # 3. Magic bytes / header check
        detected_mime = ""
        for magic, mime in cls.MAGIC_BYTES.items():
            if content.startswith(magic):
                detected_mime = mime
                break

        # WEBP check: RIFF....WEBP
        if not detected_mime and content.startswith(b"RIFF") and len(content) > 12 and content[8:12] == b"WEBP":
            detected_mime = "image/webp"

        if not detected_mime:
            # Fallback for JPEG or other valid images that PIL can open
            try:
                import io
                with Image.open(io.BytesIO(content)) as img:
                    format_to_mime = {
                        "PNG": "image/png",
                        "JPEG": "image/jpeg",
                        "WEBP": "image/webp",
                    }
                    detected_mime = format_to_mime.get(img.format, "")
            except Exception:
                pass

        if not detected_mime:
            return False, "", "Invalid or unrecognized file format header."

        return True, detected_mime, ""

    @classmethod
    def save_upload(cls, content: bytes, original_filename: str) -> tuple[str, Path]:
        """
        Saves uploaded file under a unique UUID.
        Returns: (document_id, saved_path)
        """
        doc_id = str(uuid.uuid4())
        ext = Path(original_filename).suffix.lower()
        filename = f"{doc_id}{ext}"
        target_path = settings.UPLOAD_PATH / filename

        with open(target_path, "wb") as f:
            f.write(content)

        return doc_id, target_path

    @classmethod
    def get_upload_path(cls, doc_id: str) -> Optional[Path]:
        """Finds the saved raw upload file matching doc_id regardless of extension."""
        for f in settings.UPLOAD_PATH.glob(f"{doc_id}.*"):
            if f.is_file():
                return f
        return None

    @classmethod
    def save_page_image(cls, doc_id: str, page_num: int, image: Image.Image) -> tuple[str, Path]:

        """Saves page image and returns (relative_url, path)."""
        filename = f"{doc_id}_p{page_num}.png"
        path = settings.PROCESSED_PATH / filename
        image.save(path, format="PNG", optimize=True)
        url = f"/api/v1/documents/files/processed/{filename}"
        return url, path

    @classmethod
    def save_thumbnail(cls, doc_id: str, page_num: int, image: Image.Image) -> tuple[str, Path]:
        """Saves thumbnail image and returns (relative_url, path)."""
        filename = f"{doc_id}_p{page_num}_thumb.png"
        path = settings.THUMBNAIL_PATH / filename
        image.save(path, format="PNG", optimize=True)
        url = f"/api/v1/documents/files/thumbnails/{filename}"
        return url, path

    @classmethod
    def save_document_result(cls, doc: DocumentResult) -> Path:
        """Persists DocumentResult JSON to disk."""
        target_path = settings.PROCESSED_PATH / f"{doc.document_id}.json"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(doc.model_dump_json(indent=2))
        return target_path

    @classmethod
    def load_document_result(cls, doc_id: str) -> Optional[DocumentResult]:
        target_path = settings.PROCESSED_PATH / f"{doc_id}.json"
        if not target_path.exists():
            return None
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return DocumentResult.model_validate(data)

    @classmethod
    def list_all_documents(cls) -> list[DocumentResult]:
        docs: list[DocumentResult] = []
        for file in settings.PROCESSED_PATH.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    docs.append(DocumentResult.model_validate(data))
            except Exception:
                continue
        # Sort newest first
        docs.sort(key=lambda d: d.metadata.created_at, reverse=True)
        return docs

    @classmethod
    def delete_document(cls, doc_id: str) -> bool:
        deleted = False
        # Remove uploaded raw files
        for f in settings.UPLOAD_PATH.glob(f"{doc_id}.*"):
            f.unlink(missing_ok=True)
            deleted = True
        # Remove processed pages & JSON
        for f in settings.PROCESSED_PATH.glob(f"{doc_id}*"):
            f.unlink(missing_ok=True)
            deleted = True
        # Remove thumbnails
        for f in settings.THUMBNAIL_PATH.glob(f"{doc_id}*"):
            f.unlink(missing_ok=True)
            deleted = True
        return deleted
