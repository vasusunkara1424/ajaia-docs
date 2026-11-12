import { Link } from "react-router-dom";
import type { DocumentSummary } from "../../api/types";
import { Avatar } from "../../components/ui/Avatar";
import { timeAgo } from "../../lib/format";

interface Props {
  documents: DocumentSummary[];
  emptyMessage: string;
  showOwner?: boolean;
}

export function DocumentTable({ documents, emptyMessage, showOwner = false }: Props) {
  if (documents.length === 0) return <p className="empty-state">{emptyMessage}</p>;

  return (
    <ul className="doc-list">
      {documents.map((doc) => (
        <li key={doc.id}>
          <Link to={`/documents/${doc.id}`} className="doc-row">
            <span className="doc-row__icon" aria-hidden>
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path
                  d="M6 3h8l5 5v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                />
              </svg>
            </span>
            <span className="doc-row__title">
              {doc.title}
              {doc.source_filename && <span className="tag">Imported</span>}
            </span>
            {showOwner && (
              <span className="doc-row__owner">
                <Avatar name={doc.owner.name} size={22} />
                {doc.owner.name}
              </span>
            )}
            {doc.access !== "owner" && <span className={`role-badge role-badge--${doc.access}`}>{doc.access}</span>}
            <span className="doc-row__time">{timeAgo(doc.updated_at)}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
