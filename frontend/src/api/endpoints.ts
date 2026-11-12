import { http } from "./client";
import type { DocumentDetail, DocumentList, Share, ShareRole, TokenResponse, User } from "./types";

export const authApi = {
  login: (email: string, password: string) => http.post<TokenResponse>("/auth/login", { email, password }),
  me: () => http.get<User>("/auth/me"),
};

export const documentsApi = {
  list: () => http.get<DocumentList>("/documents"),
  get: (id: number) => http.get<DocumentDetail>(`/documents/${id}`),
  create: (title?: string) => http.post<DocumentDetail>("/documents", title ? { title } : {}),
  update: (id: number, changes: { version: number; title?: string; content_html?: string }) =>
    http.patch<DocumentDetail>(`/documents/${id}`, changes),
  remove: (id: number) => http.delete(`/documents/${id}`),
  importFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return http.post<DocumentDetail>("/documents/import", form);
  },
  exportMarkdown: (id: number) => http.get<string>(`/documents/${id}/export/markdown`),
};

export const sharesApi = {
  list: (docId: number) => http.get<Share[]>(`/documents/${docId}/shares`),
  grant: (docId: number, email: string, role: ShareRole) =>
    http.put<Share>(`/documents/${docId}/shares`, { email, role }),
  revoke: (docId: number, userId: number) => http.delete(`/documents/${docId}/shares/${userId}`),
};

export const SUPPORTED_IMPORT_TYPES = [".txt", ".md", ".docx"] as const;
export const MAX_IMPORT_MB = 2;
