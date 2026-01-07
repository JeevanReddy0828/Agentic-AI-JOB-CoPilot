import type { RunRequest, RunResponse, ExtractResponse, DiffResponse } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export async function extractFile(file: File): Promise<ExtractResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/extract`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Extract failed: ${res.status}`);
  return res.json();
}

export async function runCopilot(payload: RunRequest): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`Run failed: ${res.status} ${txt}`);
  }
  return res.json();
}

export async function diffRuns(runA: string, runB: string): Promise<DiffResponse> {
  const url = `${API_BASE}/diff?run_a=${encodeURIComponent(runA)}&run_b=${encodeURIComponent(runB)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Diff failed: ${res.status}`);
  return res.json();
}
