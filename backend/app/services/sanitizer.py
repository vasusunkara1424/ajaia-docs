"""HTML sanitization.

Document content is stored as HTML and rendered by other users' browsers,
so anything we persist must be stripped to the formatting the editor
actually supports. This is the XSS boundary for the whole app.
"""

import nh3

ALLOWED_TAGS = {
    "p", "br", "hr",
    "h1", "h2", "h3",
    "strong", "b", "em", "i", "u", "s",
    "ul", "ol", "li",
    "blockquote", "code", "pre",
    "a",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


def sanitize_html(html: str) -> str:
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer nofollow",
    ).strip()
