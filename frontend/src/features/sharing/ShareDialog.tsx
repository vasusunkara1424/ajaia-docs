import { useEffect, useState, type FormEvent } from "react";
import { ApiError } from "../../api/client";
import { sharesApi } from "../../api/endpoints";
import type { DocumentDetail, Share, ShareRole } from "../../api/types";
import { useToast } from "../../components/feedback/Toast";
import { Avatar } from "../../components/ui/Avatar";
import { Modal } from "../../components/ui/Modal";

interface Props {
  document: DocumentDetail;
  onClose: () => void;
}

export function ShareDialog({ document, onClose }: Props) {
  const [shares, setShares] = useState<Share[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<ShareRole>("editor");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const notify = useToast();
  const canManage = document.permissions.can_share;

  useEffect(() => {
    sharesApi.list(document.id).then(setShares).catch(() => setError("Could not load collaborators."));
  }, [document.id]);

  const upsert = (share: Share) =>
    setShares((current) => [...current.filter((s) => s.user.id !== share.user.id), share]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const share = await sharesApi.grant(document.id, email.trim(), role);
      upsert(share);
      setEmail("");
      notify(`Shared with ${share.user.name}`, "success");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not share.");
    } finally {
      setSubmitting(false);
    }
  };

  const changeRole = async (share: Share, next: ShareRole) => {
    try {
      upsert(await sharesApi.grant(document.id, share.user.email, next));
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Could not update role.", "error");
    }
  };

  const revoke = async (share: Share) => {
    try {
      await sharesApi.revoke(document.id, share.user.id);
      setShares((current) => current.filter((s) => s.user.id !== share.user.id));
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Could not remove access.", "error");
    }
  };

  return (
    <Modal title={`Share "${document.title}"`} onClose={onClose}>
      {canManage && (
        <form className="share-form" onSubmit={submit}>
          <input
            type="email"
            required
            placeholder="Add people by email, e.g. bob@ajaia.dev"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-label="Email address"
            autoFocus
          />
          <select value={role} onChange={(e) => setRole(e.target.value as ShareRole)} aria-label="Role">
            <option value="editor">Editor</option>
            <option value="viewer">Viewer</option>
          </select>
          <button className="btn btn--primary" disabled={submitting || !email.trim()}>
            Share
          </button>
        </form>
      )}
      {error && <p className="form-error">{error}</p>}

      <h3 className="section-label">People with access</h3>
      <ul className="people-list">
        <li className="person">
          <Avatar name={document.owner.name} />
          <div className="person__info">
            <strong>{document.owner.name}</strong>
            <span>{document.owner.email}</span>
          </div>
          <span className="person__role">Owner</span>
        </li>
        {shares.map((share) => (
          <li key={share.user.id} className="person">
            <Avatar name={share.user.name} />
            <div className="person__info">
              <strong>{share.user.name}</strong>
              <span>{share.user.email}</span>
            </div>
            {canManage ? (
              <div className="person__actions">
                <select
                  value={share.role}
                  onChange={(e) => changeRole(share, e.target.value as ShareRole)}
                  aria-label={`Role for ${share.user.name}`}
                >
                  <option value="editor">Editor</option>
                  <option value="viewer">Viewer</option>
                </select>
                <button className="btn btn--ghost btn--sm" onClick={() => revoke(share)}>
                  Remove
                </button>
              </div>
            ) : (
              <span className="person__role">{share.role}</span>
            )}
          </li>
        ))}
      </ul>
      {!canManage && <p className="muted">Only the owner can change who has access.</p>}
    </Modal>
  );
}
