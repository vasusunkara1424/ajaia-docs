import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { documentsApi, MAX_IMPORT_MB, SUPPORTED_IMPORT_TYPES } from "../api/endpoints";
import type { DocumentList } from "../api/types";
import { useToast } from "../components/feedback/Toast";
import { AppHeader } from "../components/layout/AppHeader";
import { DocumentTable } from "../features/documents/DocumentTable";
import { ImportButton } from "../features/documents/ImportButton";

type Tab = "owned" | "shared";

export function DashboardPage() {
  const [data, setData] = useState<DocumentList | null>(null);
  const [tab, setTab] = useState<Tab>("owned");
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();
  const notify = useToast();

  useEffect(() => {
    documentsApi
      .list()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load documents."));
  }, []);

  const createDocument = async () => {
    setCreating(true);
    try {
      const doc = await documentsApi.create();
      navigate(`/documents/${doc.id}`, { state: { focusTitle: true } });
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Could not create document.", "error");
      setCreating(false);
    }
  };

  return (
    <div className="page">
      <AppHeader />
      <main className="dashboard">
        <div className="dashboard__head">
          <div>
            <h1>Documents</h1>
            <p className="muted small">
              Import supports {SUPPORTED_IMPORT_TYPES.join(", ")} up to {MAX_IMPORT_MB} MB.
            </p>
          </div>
          <div className="dashboard__actions">
            <ImportButton />
            <button className="btn btn--primary" onClick={createDocument} disabled={creating}>
              + New document
            </button>
          </div>
        </div>

        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={tab === "owned"} className="tab" onClick={() => setTab("owned")}>
            My documents {data && <span className="count">{data.owned.length}</span>}
          </button>
          <button role="tab" aria-selected={tab === "shared"} className="tab" onClick={() => setTab("shared")}>
            Shared with me {data && <span className="count">{data.shared.length}</span>}
          </button>
        </div>

        {error && <p className="form-error">{error}</p>}
        {!data && !error && <p className="muted">Loading…</p>}
        {data && tab === "owned" && (
          <DocumentTable documents={data.owned} emptyMessage="No documents yet. Create one or import a file." />
        )}
        {data && tab === "shared" && (
          <DocumentTable
            documents={data.shared}
            showOwner
            emptyMessage="Nothing has been shared with you yet."
          />
        )}
      </main>
    </div>
  );
}
