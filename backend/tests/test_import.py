import io

from tests.conftest import ALICE
from tests.docx_fixture import build_docx


def upload(client, auth, filename, data: bytes):
    return client.post(
        "/api/documents/import",
        files={"file": (filename, io.BytesIO(data), "application/octet-stream")},
        headers=auth(ALICE),
    )


def test_markdown_import_preserves_structure(client, auth):
    res = upload(client, auth, "meeting-notes.md", b"# Notes\n\n- **one**\n- two\n")
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "meeting-notes"
    assert body["source_filename"] == "meeting-notes.md"
    assert "<h1>Notes</h1>" in body["content_html"]
    assert "<strong>one</strong>" in body["content_html"]


def test_text_import_escapes_html_and_keeps_paragraphs(client, auth):
    res = upload(client, auth, "plain.txt", b"Hello <b>there</b>\n\nSecond paragraph")
    assert res.status_code == 201
    html = res.json()["content_html"]
    assert "&lt;b&gt;" in html  # treated as text, not markup
    assert html.count("<p>") == 2


def test_docx_import(client, auth):
    res = upload(client, auth, "report.docx", build_docx("Quarterly report"))
    assert res.status_code == 201
    assert "Quarterly report" in res.json()["content_html"]


def test_rejects_unsupported_empty_and_corrupt_files(client, auth):
    assert upload(client, auth, "image.png", b"\x89PNG....").status_code == 415
    assert upload(client, auth, "empty.md", b"   \n").status_code == 422
    assert upload(client, auth, "fake.docx", b"not a zip").status_code == 422


def test_rejects_oversized_files(client, auth):
    big = b"a" * (2 * 1024 * 1024 + 10)
    assert upload(client, auth, "big.txt", big).status_code == 413
