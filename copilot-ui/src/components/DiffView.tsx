"use client";

import { useState } from "react";
import { diffRuns } from "@/lib/api";
import type { DiffResponse } from "@/lib/types";

export default function DiffView({ runIds }: { runIds: string[] }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [loading, setLoading] = useState(false);
  const [diff, setDiff] = useState<DiffResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onDiff() {
    setErr(null);
    setDiff(null);
    if (!a || !b) {
      setErr("Pick two run IDs.");
      return;
    }
    setLoading(true);
    try {
      const res = await diffRuns(a, b);
      setDiff(res);
    } catch (e: any) {
      setErr(e?.message ?? "Diff failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl bg-white shadow-sm border border-zinc-200 p-4">
      <div className="font-semibold mb-3">Diff two runs</div>

      <div className="grid gap-2 md:grid-cols-2">
        <select value={a} onChange={(e) => setA(e.target.value)} className="border border-zinc-200 rounded-xl px-3 py-2 text-sm">
          <option value="">Select run A</option>
          {runIds.map((id) => (
            <option key={id} value={id}>{id}</option>
          ))}
        </select>

        <select value={b} onChange={(e) => setB(e.target.value)} className="border border-zinc-200 rounded-xl px-3 py-2 text-sm">
          <option value="">Select run B</option>
          {runIds.map((id) => (
            <option key={id} value={id}>{id}</option>
          ))}
        </select>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <button
          onClick={onDiff}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-zinc-900 text-white text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          {loading ? "Diffing..." : "Generate diff"}
        </button>
        {err && <div className="text-sm text-red-600">{err}</div>}
      </div>

      {diff && (
        <div className="mt-4 grid gap-4">
          <div>
            <div className="font-medium mb-2">Bullets diff</div>
            <pre className="text-xs whitespace-pre-wrap break-words bg-zinc-50 border border-zinc-200 rounded-xl p-3">
              {diff.bullets_diff || "(empty)"}
            </pre>
          </div>
          <div>
            <div className="font-medium mb-2">Cover letter diff</div>
            <pre className="text-xs whitespace-pre-wrap break-words bg-zinc-50 border border-zinc-200 rounded-xl p-3">
              {diff.cover_letter_diff || "(empty)"}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
