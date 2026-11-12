from tests.conftest import ALICE


def create(client, auth, title="Draft"):
    return client.post("/api/documents", json={"title": title}, headers=auth(ALICE)).json()


def test_create_rename_edit_and_reopen(client, auth):
    doc = create(client, auth)
    res = client.patch(
        f"/api/documents/{doc['id']}",
        json={
            "version": doc["version"],
            "title": "  Launch brief  ",
            "content_html": "<h1>Goals</h1><p><strong>Ship</strong> <u>v1</u></p><ul><li>One</li></ul>",
        },
        headers=auth(ALICE),
    )
    assert res.status_code == 200
    assert res.json()["version"] == doc["version"] + 1

    reopened = client.get(f"/api/documents/{doc['id']}", headers=auth(ALICE)).json()
    assert reopened["title"] == "Launch brief"  # whitespace trimmed
    assert "<strong>Ship</strong>" in reopened["content_html"]
    assert "<u>v1</u>" in reopened["content_html"]
    assert "<ul><li>One</li></ul>" in reopened["content_html"]


def test_stale_version_is_rejected_to_prevent_lost_updates(client, auth):
    doc = create(client, auth)
    url = f"/api/documents/{doc['id']}"
    first = client.patch(url, json={"version": doc["version"], "content_html": "<p>A</p>"}, headers=auth(ALICE))
    assert first.status_code == 200

    stale = client.patch(url, json={"version": doc["version"], "content_html": "<p>B</p>"}, headers=auth(ALICE))
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "conflict"


def test_stored_content_is_sanitized(client, auth):
    doc = create(client, auth)
    client.patch(
        f"/api/documents/{doc['id']}",
        json={
            "version": doc["version"],
            "content_html": '<p onclick="steal()">Hi<script>alert(1)</script></p><a href="javascript:x()">x</a>',
        },
        headers=auth(ALICE),
    )
    html = client.get(f"/api/documents/{doc['id']}", headers=auth(ALICE)).json()["content_html"]
    assert "script" not in html
    assert "onclick" not in html
    assert "javascript:" not in html


def test_title_validation(client, auth):
    assert client.post("/api/documents", json={"title": "   "}, headers=auth(ALICE)).status_code == 422
    assert client.post("/api/documents", json={"title": "x" * 201}, headers=auth(ALICE)).status_code == 422


def test_export_markdown(client, auth):
    doc = create(client, auth, "Notes")
    client.patch(
        f"/api/documents/{doc['id']}",
        json={"version": doc["version"], "content_html": "<h2>Agenda</h2><ul><li><strong>Budget</strong></li></ul>"},
        headers=auth(ALICE),
    )
    res = client.get(f"/api/documents/{doc['id']}/export/markdown", headers=auth(ALICE))
    assert res.status_code == 200
    assert 'filename="Notes.md"' in res.headers["content-disposition"]
    assert "## Agenda" in res.text
    assert "- **Budget**" in res.text
