"use client";

import { useEffect, useMemo, useState } from "react";
import { extractFile, runCopilot } from "@/lib/api";
import type { RunResponse, HistoryItem, RunRequest } from "@/lib/types";
import { addHistoryItem, clearHistory, loadHistory } from "@/lib/storage";
import ResultsView from "@/components/ResultsView";
import RunHistory from "@/components/RunHistory";
import DiffView from "@/components/DiffView";

export default function Page() {
  const [companyName, setCompanyName] = useState("Visa");
  const [roleTitle, setRoleTitle] = useState("Software Engineer");
  const [jobUrl, setJobUrl] = useState("");
  const [jobText, setJobText] = useState("");
  const [resumeText, setResumeText] = useState("");

  const [extracting, setExtracting] = useState(false);
  const [running, setRunning] = useState(false);

  const [result, setResult] = useState<RunResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    setHistory(loadHistory());
  }, []);

  const runIds = useMemo(() => history.map((h) => h.run_id), [history]);

  async function onUploadResume(file: File) {
    setErr(null);
    setExtracting(true);
    try {
      const res = await extractFile(file);
      setResumeText(res.text);
    } catch (e: any) {
      setErr(e?.message ?? "Extract failed");
    } finally {
      setExtracting(false);
    }
  }

  async function onRun() {
    setErr(null);
    setResult(null);
    if (!jobText.trim()) return setErr("Paste job description text.");
    if (!resumeText.trim()) return setErr("Upload resume or paste resume text.");

    setRunning(true);
    try {
      const payload: RunRequest = {
        job_text: jobText,
        resume_text: resumeText,
        company_name: companyName || null,
        role_title: roleTitle || null,
        job_url: jobUrl || null
      };

      const res = await runCopilot(payload);
      setResult(res);

      const item: HistoryItem = {
        run_id: res.run_id,
        job_id: res.job_id,
        company_name: companyName || null,
        role_title: roleTitle || null,
        job_url: jobUrl || null,
        created_at: new Date().toISOString()
      };
      addHistoryItem(item);
      setHistory(loadHistory());
    } catch (e: any) {
      setErr(e?.message ?? "Run failed");
    } finally {
      setRunning(false);
    }
  }

  function onClearHistory() {
    clearHistory();
    setHistory([]);
  }

  return (
    <main className="max-w-6xl mx-auto p-6 grid gap-6">
      <header className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-2xl font-bold">Agentic Job Application Copilot</h1>
          <p className="text-sm text-zinc-600 mt-1">
            Upload resume → paste JD → run plan/execution → get bullets + cover letter + interview pack.
          </p>
        </div>
        <div className="text-xs text-zinc-600">
          Backend: <span className="font-mono">{process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000"}</span>
        </div>
      </header>

      {err && (
        <div className="rounded-2xl border border-red-200 bg-red-50 text-red-800 p-4 text-sm">
          {err}
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-white shadow-sm border border-zinc-200 p-4">
          <div className="font-semibold mb-3">Inputs</div>

          <div className="grid gap-3">
            <div className="grid gap-2 md:grid-cols-2">
              <div>
                <label className="text-xs text-zinc-600">Company</label>
                <input
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full border border-zinc-200 rounded-xl px-3 py-2 text-sm"
                  placeholder="Visa"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-600">Role</label>
                <input
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  className="w-full border border-zinc-200 rounded-xl px-3 py-2 text-sm"
                  placeholder="Software Engineer"
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-zinc-600">Job URL (optional)</label>
              <input
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                className="w-full border border-zinc-200 rounded-xl px-3 py-2 text-sm"
                placeholder="https://..."
              />
            </div>

            <div>
              <label className="text-xs text-zinc-600">Upload resume (PDF/DOCX/TXT)</label>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) onUploadResume(f);
                }}
                className="block w-full text-sm"
              />
              <div className="text-xs text-zinc-500 mt-1">
                {extracting ? "Extracting..." : "Or paste resume text below."}
              </div>
            </div>

            <div>
              <label className="text-xs text-zinc-600">Resume text</label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                className="w-full min-h-[160px] border border-zinc-200 rounded-xl px-3 py-2 text-sm"
                placeholder="Paste resume text here..."
              />
            </div>

            <div>
              <label className="text-xs text-zinc-600">Job description text</label>
              <textarea
                value={jobText}
                onChange={(e) => setJobText(e.target.value)}
                className="w-full min-h-[180px] border border-zinc-200 rounded-xl px-3 py-2 text-sm"
                placeholder="Paste the job description here..."
              />
            </div>

            <button
              onClick={onRun}
              disabled={running || extracting}
              className="px-4 py-2 rounded-xl bg-zinc-900 text-white text-sm hover:bg-zinc-800 disabled:opacity-50"
            >
              {running ? "Running agent..." : "Run Copilot"}
            </button>

            <div className="text-xs text-zinc-500">
              Tip: Start backend first: <span className="font-mono">uvicorn app.main:app --reload</span>
            </div>
          </div>
        </div>

        <div className="grid gap-4">
          <RunHistory
            items={history}
            onSelectRunId={(id) => {
              // Only sets for diff selection via dropdowns; results are not reloaded from backend (no endpoint).
              // You can still diff runs and keep latest result on screen.
              setErr(`Selected run_id for diff: ${id}`);
              setTimeout(() => setErr(null), 1200);
            }}
            onClear={onClearHistory}
          />

          <DiffView runIds={runIds} />
        </div>
      </section>

      <section className="grid gap-4">
        <div className="flex items-center justify-between">
          <div className="font-semibold">Latest output</div>
          {result && (
            <div className="text-xs text-zinc-600 font-mono">
              run_id: {result.run_id} | job_id: {result.job_id}
            </div>
          )}
        </div>

        {result ? (
          <ResultsView result={result} />
        ) : (
          <div className="rounded-2xl bg-white shadow-sm border border-zinc-200 p-6 text-sm text-zinc-600">
            No result yet. Upload resume + paste JD and click <b>Run Copilot</b>.
          </div>
        )}
      </section>
    </main>
  );
}
