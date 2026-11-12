import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../../api/client";
import { documentsApi } from "../../api/endpoints";
import type { DocumentDetail } from "../../api/types";

export type SaveStatus = "saved" | "unsaved" | "saving" | "error" | "conflict";

interface PendingChanges {
  title?: string;
  content_html?: string;
}

const DEBOUNCE_MS = 800;

/**
 * Debounced, serialized autosave with optimistic concurrency.
 *
 * - Edits are merged into one pending patch and flushed after a short pause.
 * - Only one request is in flight at a time; edits made during a save are
 *   flushed right after it, using the version the server just returned.
 * - A 409 means someone else saved first: we stop and ask the user to reload
 *   instead of silently overwriting their work.
 */
export function useAutosave(docId: number, initialVersion: number, onSaved: (doc: DocumentDetail) => void) {
  const [status, setStatus] = useState<SaveStatus>("saved");
  const [error, setError] = useState<string | null>(null);

  const version = useRef(initialVersion);
  const pending = useRef<PendingChanges>({});
  const inFlight = useRef(false);
  const timer = useRef<number | undefined>(undefined);
  const blocked = useRef(false);
  const onSavedRef = useRef(onSaved);
  onSavedRef.current = onSaved;

  const flush = useCallback(async () => {
    window.clearTimeout(timer.current);
    if (inFlight.current || blocked.current || Object.keys(pending.current).length === 0) return;

    const changes = pending.current;
    pending.current = {};
    inFlight.current = true;
    setStatus("saving");

    try {
      const saved = await documentsApi.update(docId, { version: version.current, ...changes });
      version.current = saved.version;
      onSavedRef.current(saved);
      setError(null);
      setStatus(Object.keys(pending.current).length ? "unsaved" : "saved");
    } catch (err) {
      pending.current = { ...changes, ...pending.current }; // keep unsaved work
      const apiErr = err instanceof ApiError ? err : null;
      if (apiErr?.status === 409) {
        blocked.current = true;
        setStatus("conflict");
      } else {
        setStatus("error");
      }
      setError(apiErr?.message ?? "Could not save.");
    } finally {
      inFlight.current = false;
      if (!blocked.current && Object.keys(pending.current).length) {
        timer.current = window.setTimeout(flush, DEBOUNCE_MS);
      }
    }
  }, [docId]);

  const queue = useCallback(
    (changes: PendingChanges) => {
      pending.current = { ...pending.current, ...changes };
      setStatus("unsaved");
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(flush, DEBOUNCE_MS);
    },
    [flush],
  );

  // Warn before closing the tab with unsaved work; flush when leaving the page.
  useEffect(() => {
    const beforeUnload = (e: BeforeUnloadEvent) => {
      if (Object.keys(pending.current).length || inFlight.current) e.preventDefault();
    };
    window.addEventListener("beforeunload", beforeUnload);
    return () => {
      window.removeEventListener("beforeunload", beforeUnload);
      void flush();
    };
  }, [flush]);

  return { status, error, queue, flush };
}
