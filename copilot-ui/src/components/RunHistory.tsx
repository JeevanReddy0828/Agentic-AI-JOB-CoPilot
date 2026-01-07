import type { HistoryItem } from "@/lib/types";

export default function RunHistory({
  items,
  onSelectRunId,
  onClear
}: {
  items: HistoryItem[];
  onSelectRunId: (runId: string) => void;
  onClear: () => void;
}) {
  return (
    <div className="rounded-2xl bg-white shadow-sm border border-zinc-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="font-semibold">Run history (local)</div>
        <button
          onClick={onClear}
          className="text-xs px-3 py-1 rounded-full border border-zinc-200 hover:bg-zinc-50"
        >
          Clear
        </button>
      </div>

      {items.length === 0 ? (
        <div className="text-sm text-zinc-600">No runs yet.</div>
      ) : (
        <div className="grid gap-2">
          {items.map((h) => (
            <button
              key={h.run_id}
              onClick={() => onSelectRunId(h.run_id)}
              className="text-left rounded-xl border border-zinc-200 hover:bg-zinc-50 p-3"
            >
              <div className="text-sm font-medium">{h.company_name || "(Company)"} — {h.role_title || "(Role)"}</div>
              <div className="text-xs text-zinc-600 break-all">run_id: {h.run_id}</div>
              <div className="text-xs text-zinc-600 break-all">job_id: {h.job_id}</div>
              <div className="text-xs text-zinc-500">{new Date(h.created_at).toLocaleString()}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
