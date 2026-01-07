import type { RunResponse } from "@/lib/types";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl bg-white shadow-sm border border-zinc-200 p-4">
      <div className="font-semibold text-zinc-900 mb-2">{title}</div>
      <div className="text-sm text-zinc-800">{children}</div>
    </div>
  );
}

export default function ResultsView({ result }: { result: RunResponse }) {
  return (
    <div className="grid gap-4">
      <Section title="JD Summary">
        <pre className="whitespace-pre-wrap break-words">{JSON.stringify(result.jd_summary, null, 2)}</pre>
      </Section>

      <Section title="ATS Keywords">
        <div className="flex flex-wrap gap-2">
          {result.ats_keywords?.map((k) => (
            <span key={k} className="text-xs bg-zinc-100 border border-zinc-200 rounded-full px-2 py-1">
              {k}
            </span>
          ))}
        </div>
      </Section>

      <Section title="Company Research">
        <div className="mb-2">{result.company_research?.overview || "(No overview)"}</div>
        <div className="grid gap-1">
          {(result.company_research?.recent_news || []).map((n, idx) => (
            <a
              key={idx}
              href={n.url}
              target="_blank"
              rel="noreferrer"
              className="text-sm underline text-zinc-900 hover:text-zinc-700"
            >
              {n.title}
            </a>
          ))}
        </div>
      </Section>

      <Section title="Tailored Resume Bullets">
        <ul className="list-disc pl-5 space-y-2">
          {(result.tailored_resume_bullets || []).map((b, idx) => (
            <li key={idx}>{b}</li>
          ))}
        </ul>
      </Section>

      <Section title="Cover Letter">
        <pre className="whitespace-pre-wrap break-words">{result.cover_letter}</pre>
      </Section>

      <Section title="Interview Pack">
        <div className="grid gap-3">
          <div>
            <div className="font-medium mb-1">STAR Stories</div>
            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(result.interview_pack?.star_stories || [], null, 2)}</pre>
          </div>
          <div>
            <div className="font-medium mb-1">Behavioral Qs</div>
            <ul className="list-disc pl-5 space-y-1">
              {(result.interview_pack?.behavioral_qs || []).map((q, idx) => (
                <li key={idx}>{q}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="font-medium mb-1">Technical Qs</div>
            <ul className="list-disc pl-5 space-y-1">
              {(result.interview_pack?.technical_qs || []).map((q, idx) => (
                <li key={idx}>{q}</li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      <Section title="Verifier Report">
        <pre className="whitespace-pre-wrap break-words">{JSON.stringify(result.verifier_report, null, 2)}</pre>
      </Section>

      <Section title="Execution Log (State Machine)">
        <pre className="whitespace-pre-wrap break-words">{JSON.stringify(result.execution_log, null, 2)}</pre>
      </Section>
    </div>
  );
}
