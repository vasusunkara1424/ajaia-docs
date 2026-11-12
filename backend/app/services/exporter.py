"""Export document HTML to other formats."""

import re

from markdownify import markdownify


def html_to_markdown(content_html: str) -> str:
    md = markdownify(content_html, heading_style="ATX", bullets="-", strong_em_symbol="*")
    # Collapse the extra blank lines markdownify leaves between blocks.
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def safe_filename(title: str, extension: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9 _-]+", "", title).strip().replace(" ", "_") or "document"
    return f"{stem[:80]}.{extension}"
