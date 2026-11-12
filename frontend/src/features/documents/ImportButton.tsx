import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../../api/client";
import { documentsApi, MAX_IMPORT_MB, SUPPORTED_IMPORT_TYPES } from "../../api/endpoints";
import { useToast } from "../../components/feedback/Toast";

/** Upload a .txt / .md / .docx file and open it as a new editable document. */
export function ImportButton() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const notify = useToast();

  const handleFile = async (file: File) => {
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    // Client-side checks give instant feedback; the server enforces the same rules.
    if (!SUPPORTED_IMPORT_TYPES.includes(ext as (typeof SUPPORTED_IMPORT_TYPES)[number])) {
      notify(`Unsupported file type. Use ${SUPPORTED_IMPORT_TYPES.join(", ")}.`, "error");
      return;
    }
    if (file.size > MAX_IMPORT_MB * 1024 * 1024) {
      notify(`File is larger than ${MAX_IMPORT_MB} MB.`, "error");
      return;
    }
    setBusy(true);
    try {
      const doc = await documentsApi.importFile(file);
      notify(`Imported "${doc.title}"`, "success");
      navigate(`/documents/${doc.id}`);
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Import failed.", "error");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <>
      <button
        className="btn btn--secondary"
        onClick={() => inputRef.current?.click()}
        disabled={busy}
        title={`Supported: ${SUPPORTED_IMPORT_TYPES.join(", ")} (max ${MAX_IMPORT_MB} MB)`}
      >
        {busy ? "Importing…" : "Import file"}
      </button>
      <input
        ref={inputRef}
        type="file"
        hidden
        accept={SUPPORTED_IMPORT_TYPES.join(",")}
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
    </>
  );
}
