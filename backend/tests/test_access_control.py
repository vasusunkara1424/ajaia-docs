"""The sharing model is the riskiest logic in the app, so it gets the most coverage.

Matrix under test (see app/services/access.py):
    owner  -> view, edit, share, delete
    editor -> view, edit
    viewer -> view only
    other  -> 404 (existence is not revealed)
"""

import pytest

from tests.conftest import ALICE, BOB, CAROL


@pytest.fixture
def doc(client, auth):
    res = client.post("/api/documents", json={"title": "Q4 plan"}, headers=auth(ALICE))
    assert res.status_code == 201
    return res.json()


def share(client, auth, doc_id, email, role):
    return client.put(
        f"/api/documents/{doc_id}/shares", json={"email": email, "role": role}, headers=auth(ALICE)
    )


def edit(client, auth, email, doc, html="<p>changed</p>"):
    current = client.get(f"/api/documents/{doc['id']}", headers=auth(email)).json()
    return client.patch(
        f"/api/documents/{doc['id']}",
        json={"version": current["version"], "content_html": html},
        headers=auth(email),
    )


def test_unauthenticated_requests_are_rejected(client):
    assert client.get("/api/documents").status_code == 401


def test_stranger_cannot_see_or_find_document(client, auth, doc):
    res = client.get(f"/api/documents/{doc['id']}", headers=auth(CAROL))
    assert res.status_code == 404
    listing = client.get("/api/documents", headers=auth(CAROL)).json()
    assert listing == {"owned": [], "shared": []}


def test_viewer_can_read_but_not_edit(client, auth, doc):
    assert share(client, auth, doc["id"], BOB, "viewer").status_code == 200

    res = client.get(f"/api/documents/{doc['id']}", headers=auth(BOB))
    assert res.status_code == 200
    assert res.json()["access"] == "viewer"
    assert res.json()["permissions"] == {"can_edit": False, "can_share": False, "can_delete": False}

    assert edit(client, auth, BOB, doc).status_code == 403


def test_editor_can_edit_but_not_share_or_delete(client, auth, doc):
    share(client, auth, doc["id"], BOB, "editor")

    assert edit(client, auth, BOB, doc).status_code == 200
    res = client.put(
        f"/api/documents/{doc['id']}/shares",
        json={"email": CAROL, "role": "viewer"},
        headers=auth(BOB),
    )
    assert res.status_code == 403
    assert client.delete(f"/api/documents/{doc['id']}", headers=auth(BOB)).status_code == 403


def test_shared_document_appears_in_shared_section_not_owned(client, auth, doc):
    share(client, auth, doc["id"], BOB, "viewer")
    bob = client.get("/api/documents", headers=auth(BOB)).json()
    alice = client.get("/api/documents", headers=auth(ALICE)).json()

    assert [d["id"] for d in bob["shared"]] == [doc["id"]]
    assert bob["owned"] == []
    assert [d["id"] for d in alice["owned"]] == [doc["id"]]


def test_role_can_be_upgraded_and_access_revoked(client, auth, doc):
    share(client, auth, doc["id"], BOB, "viewer")
    share(client, auth, doc["id"], BOB, "editor")  # idempotent upsert, not a duplicate
    shares = client.get(f"/api/documents/{doc['id']}/shares", headers=auth(ALICE)).json()
    assert len(shares) == 1 and shares[0]["role"] == "editor"

    bob_id = shares[0]["user"]["id"]
    res = client.delete(f"/api/documents/{doc['id']}/shares/{bob_id}", headers=auth(ALICE))
    assert res.status_code == 204
    assert client.get(f"/api/documents/{doc['id']}", headers=auth(BOB)).status_code == 404


def test_sharing_validation(client, auth, doc):
    assert share(client, auth, doc["id"], "nobody@ajaia.dev", "viewer").status_code == 404
    assert share(client, auth, doc["id"], ALICE, "viewer").status_code == 422
    assert share(client, auth, doc["id"], BOB, "admin").status_code == 422
