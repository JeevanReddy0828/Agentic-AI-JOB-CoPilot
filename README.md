# Agentic Job Application Copilot

An end-to-end **agentic AI system** that helps you tailor job applications using a **plan → execute → verify** workflow.

The project consists of:
- **Backend (FastAPI + OpenAI)**: Orchestrates agent planning, tool execution, grounding checks, and persistence.
- **Frontend (Next.js + Tailwind)**: Minimal UI to upload resumes, paste job descriptions, run the agent, view results, compare runs, and track history.

---

## 📁 Repository Structure

```
agentic-job-copilot/
│
├── app/                      # FastAPI backend
│   ├── agent.py               # Agent loop (plan → execute → state machine)
│   ├── main.py                # FastAPI routes
│   ├── tools.py               # Tool functions (planning, keyword extraction, grounding, web search)
│   ├── ingest.py              # PDF/DOCX/TXT text extraction
│   ├── scoring.py             # ATS scoring logic
│   ├── diffs.py               # Diff utilities
│   ├── storage.py             # SQLite persistence
│   ├── schemas.py             # Pydantic request/response models
│   └── prompts.py             # System + task prompts
│
├── copilot-ui/                # Next.js frontend
│   ├── src/
│   │   ├── app/               # App Router pages/layout
│   │   ├── components/        # UI components (Results, Diff, History)
│   │   └── lib/               # API client + local storage helpers
│   ├── public/
│   ├── package.json
│   └── tailwind.config.ts
│
├── data/                      # Runtime data (SQLite DB, ignored by git)
│
├── .gitignore                 # Root gitignore (Python + Node)
├── .env.example               # Environment variable template
├── requirements.txt           # Backend dependencies
└── README.md                  # This file
```

---

## 🚀 Backend: FastAPI Agent

### Features
- **Agentic planning** via `create_action_plan()`
- **Step-by-step execution** with status tracking
- **Grounding verification** to prevent hallucinations
- **ATS keyword extraction + scoring**
- **Company research tool** (optional, via Tavily)
- **Run versioning and diffs** stored in SQLite

### Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Visit: http://127.0.0.1:8000/docs

---

## 🎨 Frontend: Next.js UI

### Features
- Upload resume (PDF / DOCX / TXT)
- Paste job description
- Run agent and view outputs
- Local run history (browser storage)
- Diff two runs (resume bullets + cover letter)

### Setup
```bash
cd copilot-ui
npm install
npm run dev
```

Optional `.env.local`:
```env
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

Visit: http://localhost:3000

---

## 🧠 Typical Workflow

1. Start backend (`uvicorn ...`)
2. Start frontend (`npm run dev`)
3. Upload resume or paste resume text
4. Paste job description
5. Run copilot
6. Review:
   - Tailored resume bullets
   - Cover letter
   - Interview pack
   - Execution log (agent steps)
7. Run again → compare with diff

---

## ⚠️ Notes
- First run may take ~30–90 seconds due to multiple LLM calls
- Ensure `OPENAI_API_KEY` is set in `.env`

---

## 📌 Future Extensions
- Auth + user accounts
- Persistent run history via backend API
- Resume export (PDF/DOCX)
- Multi-agent decomposition
- Recruiter-specific templates

---

