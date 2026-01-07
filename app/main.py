from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile

from app.schemas import RunRequest, RunResponse, ScoreRequest, DiffResponse
from app.agent import run_copilot
from app.storage import init_db, upsert_job, save_artifact, load_run
from app.ingest import extract_text
from app.scoring import ats_score
from app.diffs import unified_diff
from app.tools import extract_keywords

app = FastAPI(title="Agentic Job Application Copilot")

@app.on_event("startup")
def _startup():
    init_db()

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    suffix = "." + file.filename.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    text = extract_text(tmp_path)
    return {"filename": file.filename, "text": text}

@app.post("/run", response_model=RunResponse)
async def run(req: RunRequest):
    job_id = upsert_job(
        job_url=req.job_url,
        company=req.company_name,
        role=req.role_title,
        jd_text=req.job_text,
    )

    payload = await run_copilot(
        job_text=req.job_text,
        resume_text=req.resume_text,
        company_name=req.company_name,
        role_title=req.role_title,
        job_url=req.job_url,
    )

    run_id = save_artifact(job_id, payload)
    return {**payload, "run_id": run_id, "job_id": job_id}

@app.post("/score")
def score(req: ScoreRequest):
    keywords = extract_keywords(req.job_text)
    return {"ats_keywords": keywords, "scorecard": ats_score(keywords, req.resume_text)}

@app.get("/diff", response_model=DiffResponse)
def diff(run_a: str, run_b: str):
    a = load_run(run_a)
    b = load_run(run_b)
    if not a or not b:
        raise HTTPException(status_code=404, detail="run_id not found")

    a_bullets = "\n".join(a.get("tailored_resume_bullets", []))
    b_bullets = "\n".join(b.get("tailored_resume_bullets", []))
    a_cl = a.get("cover_letter", "")
    b_cl = b.get("cover_letter", "")

    return {
        "bullets_diff": unified_diff(a_bullets, b_bullets, "run_a_bullets", "run_b_bullets"),
        "cover_letter_diff": unified_diff(a_cl, b_cl, "run_a_cover", "run_b_cover"),
    }
