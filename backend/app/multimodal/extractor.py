"""Extract textual content from uploaded multimodal files.

Every optional dependency (PDF, DOCX, OCR, image handling) is imported lazily
and guarded, so the running project is never broken by a missing library —
the caller just receives a descriptive ``note`` when an extraction path is
not available.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xml",
    ".yaml",
    ".yml",
    ".log",
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sql",
    ".sh",
    ".bat",
    ".ps1",
    ".ini",
    ".cfg",
    ".toml",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".opus", ".flac", ".m4a", ".aac", ".webm"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}


@dataclass
class ExtractedAttachment:
    """Result of extracting content from a single uploaded file."""

    filename: str
    kind: str  # text | image | audio | video | document | other
    extracted: str = ""
    note: str = ""


def _decode_text(data: bytes) -> str:
    """Decode raw bytes as UTF-8 (with graceful fallbacks) for text files."""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, ValueError):
            continue
    return ""


def _extract_pdf(filename: str, data: bytes) -> ExtractedAttachment:
    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except Exception:
        return ExtractedAttachment(
            filename,
            "document",
            "",
            "PDF text extraction is not available (install 'pypdf'). The PDF was attached for reference.",
        )

    try:
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return ExtractedAttachment(
            filename,
            "document",
            text,
            "PDF text extracted." if text.strip() else "The PDF contained no extractable text.",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return ExtractedAttachment(
            filename,
            "document",
            "",
            f"PDF text extraction failed: {exc}",
        )


def _extract_docx(filename: str, data: bytes) -> ExtractedAttachment:
    try:
        from docx import Document  # type: ignore[import-not-found]
    except Exception:
        return ExtractedAttachment(
            filename,
            "document",
            "",
            "DOCX text extraction is not available (install 'python-docx'). The document was attached for reference.",
        )

    try:
        document = Document(io.BytesIO(data))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return ExtractedAttachment(
            filename,
            "document",
            text,
            "DOCX text extracted." if text.strip() else "The document contained no extractable text.",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return ExtractedAttachment(
            filename,
            "document",
            "",
            f"DOCX text extraction failed: {exc}",
        )


def _extract_image(filename: str, data: bytes) -> ExtractedAttachment:
    try:
        import pytesseract  # type: ignore[import-not-found]
        from PIL import Image  # type: ignore[import-not-found]
    except Exception:
        return ExtractedAttachment(
            filename,
            "image",
            "",
            "Image OCR is not available (install 'pytesseract' and Tesseract). The image was attached for reference.",
        )

    try:
        image = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(image)
        return ExtractedAttachment(
            filename,
            "image",
            text,
            "OCR text extracted." if text.strip() else "No readable text was detected in the image.",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return ExtractedAttachment(
            filename,
            "image",
            "",
            f"Image OCR failed: {exc}",
        )


def _extract_audio(filename: str) -> ExtractedAttachment:
    return ExtractedAttachment(
        filename,
        "audio",
        "",
        "Audio transcription is not available in this environment; the recording was attached for reference. "
        "For voice input, use the in-browser voice (microphone) button instead.",
    )


def _extract_video(filename: str) -> ExtractedAttachment:
    return ExtractedAttachment(
        filename,
        "video",
        "",
        "Video transcription is not available in this environment; the video was attached for reference. "
        "Describe the video with text or voice so it can be turned into a project.",
    )


def extract_attachment(filename: str, data: bytes) -> ExtractedAttachment:
    """Extract text/reference content from one uploaded file based on its extension."""
    suffix = Path(filename or "").suffix.lower()

    if suffix in TEXT_EXTENSIONS:
        return ExtractedAttachment(filename, "text", _decode_text(data))

    if suffix in IMAGE_EXTENSIONS:
        return _extract_image(filename, data)

    if suffix in AUDIO_EXTENSIONS:
        return _extract_audio(filename)

    if suffix in VIDEO_EXTENSIONS:
        return _extract_video(filename)

    if suffix == ".pdf":
        return _extract_pdf(filename, data)

    if suffix == ".docx":
        return _extract_docx(filename, data)

    if suffix in {".doc", ".odt", ".rtf", ".pptx", ".xlsx"}:
        return ExtractedAttachment(
            filename,
            "document",
            "",
            f"{suffix} files are not parsed in this environment; the file was attached for reference.",
        )

    return ExtractedAttachment(
        filename,
        "other",
        "",
        "Unknown file type; the file was attached for reference.",
    )
