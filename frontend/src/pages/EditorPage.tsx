import Placeholder from "@tiptap/extension-placeholder";
import Underline from "@tiptap/extension-underline";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { documentsApi } from "../api/endpoints";
import type { DocumentDetail } from "../api/types";
import { useToast } from "../components/feedback/Toast";
import { AppHeader } from "../components/layout/AppHeader";
import { Toolbar } from "../features/editor/Toolbar";
import { useAutosave, type SaveStatus } from "../features/editor/useAutosave";
import { ShareDialog } from "../features/sharing/ShareDialog";
import { downloadText } from "../lib/format";

export function EditorPage() {
  const { id } = useParams();
  const docId = Number(id);
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    setDoc(null);
    setLoadError(null);
    if (!Number.isInteger(docId)) {
      setLoadError("Document not found.");
      return;
    }
    documentsApi
      .get(docId)
      .then(setDoc)
      .catch((err) => setLoadError(err instanceof ApiError ? err.message : "Could not open document."));
  }, [docId]);

  if (loadError) {
    return (
      <div className="page">
        <AppHeader />
        <main className="centered">
          <h1>Can't open this document</h1>
          <p className="muted">{loadError}</p>
          <Link to="/" className="btn btn--primary">
            Back to documents
          </Link>
        </main>
      </div>
    );
  }
  if (!doc) {
    return (
      <div className="page">
        <AppHeader />
        <main className="centered muted">Loading…</main>
      </div>
    );
  }
  // Keyed so switching documents fully resets editor + autosave state.
  return <DocumentEditor key={doc.id} initial={doc} />;
}

function DocumentEditor({ initial }: { initial: DocumentDetail }) {
  const [doc, setDoc] = useState(initial);
  const [title, setTitle] = useState(initial.title);
  const [sharing, setSharing] = useState(false);
  const titleRef = useRef<HTMLInputElement>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const notify = useToast();
  const editable = initial.permissions.can_edit;

  const onSaved = useCallback((saved: DocumentDetail) => setDoc(saved), []);
  const { status, error, queue } = useAutosave(initial.id, initial.version, onSaved);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Underline,
      Placeholder.configure({ placeholder: "Start writing…" }),
    ],
    content: initial.content_html,
    editable,
    onUpdate: ({ editor }) => queue({ content_html: editor.getHTML() }),
  });

  useEffect(() => {
    if ((location.state as { focusTitle?: boolean } | null)?.focusTitle) titleRef.current?.select();
  }, [location.state]);

  const commitTitle = () => {
    const next = title.trim();
    if (!next) {
      setTitle(doc.title); // empty titles are not allowed; revert
      return;
    }
    if (next !== doc.title) queue({ title: next });
  };

  const exportMarkdown = async () => {
    try {
      const md = await documentsApi.exportMarkdown(doc.id);
      downloadText(`${title.trim() || "document"}.md`, md);
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Export failed.", "error");
    }
  };

  const deleteDocument = async () => {
    if (!window.confirm(`Delete "${doc.title}"? This can't be undone.`)) return;
    try {
      await documentsApi.remove(doc.id);
      notify("Document deleted", "success");
      navigate("/");
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Delete failed.", "error");
    }
  };

  return (
    <div className="page page--editor">
      <AppHeader>
        <div className="doc-header">
          <input
            ref={titleRef}
            className="doc-title"
            value={title}
            maxLength={200}
            readOnly={!editable}
            aria-label="Document title"
            onChange={(e) => setTitle(e.target.value)}
            onBlur={commitTitle}
            onKeyDown={(e) => e.key === "Enter" && (e.currentTarget as HTMLInputElement).blur()}
          />
          <SaveIndicator status={status} error={error} />
        </div>
      </AppHeader>

      <div className="editor-bar">
        {editable && editor ? <Toolbar editor={editor} /> : <span className="viewonly">View only</span>}
        <div className="editor-bar__actions">
          <button className="btn btn--ghost btn--sm" onClick={exportMarkdown}>
            Export .md
          </button>
          {doc.permissions.can_delete && (
            <button className="btn btn--ghost btn--sm btn--danger" onClick={deleteDocument}>
              Delete
            </button>
          )}
          <button className="btn btn--primary btn--sm" onClick={() => setSharing(true)}>
            {doc.permissions.can_share ? "Share" : "People"}
          </button>
        </div>
      </div>

      {status === "conflict" && (
        <div className="banner banner--warn">
          {error}{" "}
          <button className="link-btn" onClick={() => window.location.reload()}>
            Reload document
          </button>
        </div>
      )}

      <main className="paper-wrap">
        <article className="paper">
          <EditorContent editor={editor} className="prose" />
        </article>
        <p className="paper-meta">
          Owned by {doc.owner.name}
          {doc.access !== "owner" && ` · You are ${doc.access === "editor" ? "an editor" : "a viewer"}`}
          {doc.source_filename && ` · Imported from ${doc.source_filename}`}
        </p>
      </main>

      {sharing && <ShareDialog document={doc} onClose={() => setSharing(false)} />}
    </div>
  );
}

const STATUS_TEXT: Record<SaveStatus, string> = {
  saved: "All changes saved",
  unsaved: "Unsaved changes",
  saving: "Saving…",
  error: "Save failed, retrying on next edit",
  conflict: "Out of date",
};

function SaveIndicator({ status, error }: { status: SaveStatus; error: string | null }) {
  return (
    <span className={`save-indicator save-indicator--${status}`} title={error ?? undefined}>
      {STATUS_TEXT[status]}
    </span>
  );
}
