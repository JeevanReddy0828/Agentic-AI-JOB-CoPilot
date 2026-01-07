# Agentic Job Application Copilot (Plan → Execute → Verify)

An agentic AI system that:
- Plans a workflow (`create_action_plan`)
- Executes each step with tool-calling + LLM reasoning
- Tracks step status (simple state machine)
- Produces grounded resume bullets, cover letter, interview pack, ATS score, and diffs

## Features
- `/extract` upload PDF/DOCX/TXT and extract text
- `/run` agentic plan+execute run, persists artifacts per job
- `/score` keyword coverage ATS scoring
- `/diff` compare two runs

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# mac/linux:
# source .venv/bin/activate

python.exe -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY (and optional TAVILY_API_KEY)
uvicorn app.main:app --reload
```

## Quick Test
### Extract resume text from PDF
```bash
curl -X POST "http://127.0.0.1:8000/extract" -F "file=@resume.pdf"
```

### Run the agent
```bash
curl -X POST "http://127.0.0.1:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "job_url":"https://example.com/jd",
    "company_name":"Visa",
    "role_title":"Software Engineer",
    "job_text":"PASTE JOB DESCRIPTION TEXT",
    "resume_text":"PASTE RESUME TEXT"
  }'
```

### Score only
```bash
curl -X POST "http://127.0.0.1:8000/score" \
  -H "Content-Type: application/json" \
  -d '{"job_text":"PASTE JD","resume_text":"PASTE RESUME"}'
```

### Diff two runs
```bash
curl "http://127.0.0.1:8000/diff?run_a=RUN_ID_1&run_b=RUN_ID_2"
```

## Notes
- If you don't set `TAVILY_API_KEY`, web research will return an error message and the agent will proceed without it.
- This project is intentionally minimal; you can add a UI later (Next.js).
