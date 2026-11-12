// Mirrors the backend Pydantic schemas (backend/app/schemas).

export interface User {
  id: number;
  email: string;
  name: string;
}

export type AccessLevel = "owner" | "editor" | "viewer";
export type ShareRole = "viewer" | "editor";

export interface DocumentSummary {
  id: number;
  title: string;
  owner: User;
  access: AccessLevel;
  updated_at: string;
  source_filename: string | null;
}

export interface DocumentDetail extends DocumentSummary {
  content_html: string;
  version: number;
  permissions: { can_edit: boolean; can_share: boolean; can_delete: boolean };
}

export interface DocumentList {
  owned: DocumentSummary[];
  shared: DocumentSummary[];
}

export interface Share {
  user: User;
  role: ShareRole;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
