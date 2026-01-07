import type { HistoryItem } from "@/lib/types";

const KEY = "copilot_run_history_v1";

export function loadHistory(): HistoryItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as HistoryItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveHistory(items: HistoryItem[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(items));
}

export function addHistoryItem(item: HistoryItem) {
  const items = loadHistory();
  items.unshift(item);
  // de-dupe by run_id
  const seen = new Set<string>();
  const deduped = items.filter((x) => (seen.has(x.run_id) ? false : seen.add(x.run_id)));
  saveHistory(deduped.slice(0, 50));
}

export function clearHistory() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEY);
}
