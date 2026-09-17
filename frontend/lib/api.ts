import { DocumentResult, OCRBlock, ProcessingSummary } from "../types/document";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getDownloadUrl(docId: string): string {
  return `${API_BASE}/api/v1/documents/${docId}/download`;
}

export function getExportUrl(docId: string, format: string): string {
  return `${API_BASE}/api/v1/documents/${docId}/export/${format}`;
}

export async function compareDocuments(
  docAId: string,
  docBId: string
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/documents/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_a_id: docAId, doc_b_id: docBId }),
  });

  if (!res.ok) {
    let errorMsg = "Comparison failed";
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function askDocNova(
  docId: string,
  question: string
): Promise<{ question: string; answer: string; sources: any[]; confidence: number }> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${docId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    let errorMsg = "Failed to get answer";
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentResult> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = `Upload failed with status ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function getDocument(id: string): Promise<DocumentResult> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to load document: ${res.statusText}`);
  }

  return res.json();
}

export async function listDocuments(): Promise<DocumentResult[]> {
  const res = await fetch(`${API_BASE}/api/v1/documents`, {
    cache: "no-store",
  });

  if (!res.ok) {
    return [];
  }

  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error(`Failed to delete document: ${res.statusText}`);
  }
}

export async function searchDocument(
  id: string,
  query: string
): Promise<{ query: string; total_matches: number; matches: any[] }> {
  const res = await fetch(
    `${API_BASE}/api/v1/documents/${id}/search?q=${encodeURIComponent(query)}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    return { query, total_matches: 0, matches: [] };
  }
  return res.json();
}

export function getFileUrl(path: string): string {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${API_BASE}${path}`;
}

export async function updateBlock(
  docId: string,
  blockId: string,
  updates: { text?: string; layout_type?: string; confidence?: number; bbox?: any }
): Promise<DocumentResult> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${docId}/blocks/${blockId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });

  if (!res.ok) {
    let errorMsg = `Failed to update block: ${res.statusText}`;
    try {
      const err = await res.json();
      if (err.detail) errorMsg = err.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  const data = await res.json();
  return data.document;
}

