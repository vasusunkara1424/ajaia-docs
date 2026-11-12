"""Convert uploaded files into sanitized document HTML.

Supported: .txt, .md, .docx (max size set in settings).
Each format is converted to HTML, then passed through the same sanitizer
as editor content, so imported documents obey exactly the same rules.
"""

import html
import io
import re
from dataclasses import dataclass
from pathlib import PurePath

import mammoth
import markdown

from app.core.config import get_settings
from app.core.errors import PayloadTooLargeError, UnsupportedFileError, ValidationFailedError
from app.services.sanitizer import sanitize_html

SUPPORTED_EXTENSIONS = (".txt", ".md", ".docx")
_ZIP_MAGIC = b"PK\x03\x04"


@dataclass(frozen=True)
class ImportedFile:
    title: str
    content_html: str
    source_filename: str


def import_file(filename: str, data: bytes) -> ImportedFile:
    name = PurePath(filename or "").name
    extension = PurePath(name).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError(
            f"Unsupported file type '{extension or 'none'}'. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}."
        )
    max_bytes = get_settings().max_upload_bytes
    if len(data) > max_bytes:
        raise PayloadTooLargeError(f"File is larger than {max_bytes // (1024 * 1024)} MB.")
    if not data.strip():
        raise ValidationFailedError("The uploaded file is empty.")

    converters = {".txt": _txt_to_html, ".md": _markdown_to_html, ".docx": _docx_to_html}
    content_html = sanitize_html(converters[extension](data))
    if not content_html:
        raise ValidationFailedError("No readable content was found in the file.")

    title = PurePath(name).stem.strip()[:200] or "Imported document"
    return ImportedFile(title=title, content_html=content_html, source_filename=name)


def _decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationFailedError("Text files must be UTF-8 encoded.") from exc


def _txt_to_html(data: bytes) -> str:
    text = _decode_text(data).replace("\r\n", "\n")
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{html.escape(p.strip()).replace(chr(10), '<br>')}</p>" for p in paragraphs)


def _markdown_to_html(data: bytes) -> str:
    return markdown.markdown(_decode_text(data), extensions=["extra", "sane_lists"])


def _docx_to_html(data: bytes) -> str:
    if not data.startswith(_ZIP_MAGIC):
        raise ValidationFailedError("This file is not a valid .docx document.")
    try:
        result = mammoth.convert_to_html(io.BytesIO(data))
    except Exception as exc:  # mammoth raises a variety of zip/xml errors
        raise ValidationFailedError("This .docx file could not be read.") from exc
    return result.value
