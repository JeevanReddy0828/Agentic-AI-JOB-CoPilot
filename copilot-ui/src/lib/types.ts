export type RunRequest = {
  job_text: string;
  resume_text: string;
  company_name?: string | null;
  role_title?: string | null;
  job_url?: string | null;
};

export type RunResponse = {
  jd_summary: any;
  ats_keywords: string[];
  company_research: { overview: string; recent_news: { title: string; url: string }[] };
  tailored_resume_bullets: string[];
  cover_letter: string;
  interview_pack: {
    star_stories: any[];
    behavioral_qs: string[];
    technical_qs: string[];
  };
  verifier_report: any;
  execution_log: any;
  run_id: string;
  job_id: string;
};

export type ExtractResponse = { filename: string; text: string };

export type DiffResponse = { bullets_diff: string; cover_letter_diff: string };

export type HistoryItem = {
  run_id: string;
  job_id: string;
  company_name?: string | null;
  role_title?: string | null;
  job_url?: string | null;
  created_at: string; // ISO
};
