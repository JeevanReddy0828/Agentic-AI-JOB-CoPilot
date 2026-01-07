import os
import re
from typing import Dict, List, Any
import httpx
import uuid

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def create_action_plan(company_name: str | None, role_title: str | None, job_url: str | None) -> Dict[str, Any]:
    """Return a deterministic JSON plan the agent will execute.
    Each step has:
      - id
      - name
      - kind: tool|llm
      - status: pending|done|skipped|failed
      - note: optional
    """
    steps = [
        {"id": "S1", "name": "Extract ATS keywords from job text", "kind": "tool", "tool": "extract_keywords", "status": "pending"},
        {"id": "S2", "name": "Extract evidence claims from resume", "kind": "tool", "tool": "extract_resume_claims", "status": "pending"},
        {"id": "S3", "name": "Company research via web search", "kind": "tool", "tool": "web_search", "status": "pending",
         "note": "Skip if company_name is missing or web API key unavailable."},
        {"id": "S4", "name": "Summarize JD into must-haves and nice-to-haves", "kind": "llm", "status": "pending"},
        {"id": "S5", "name": "Draft ATS-optimized resume bullets grounded in resume", "kind": "llm", "status": "pending"},
        {"id": "S6", "name": "Run grounding check and revise flagged bullets", "kind": "tool", "tool": "check_grounding", "status": "pending"},
        {"id": "S7", "name": "Write role-specific cover letter using JD + resume + research", "kind": "llm", "status": "pending"},
        {"id": "S8", "name": "Generate interview pack (STAR stories + Qs)", "kind": "llm", "status": "pending"},
        {"id": "S9", "name": "Produce verifier report (what was grounded vs neutralized)", "kind": "llm", "status": "pending"},
    ]
    return {
        "plan_id": str(uuid.uuid4()),
        "context": {"company_name": company_name, "role_title": role_title, "job_url": job_url},
        "steps": steps,
    }

def extract_keywords(job_text: str) -> List[str]:
    terms = re.findall(r"[A-Za-z][A-Za-z\+\#\.]{1,30}", job_text)
    common = {
        "the","and","with","for","you","our","are","will","have","this","that","from",
        "to","in","on","of","a","an","as","by","or","we","is","be","at"
    }
    keep = []
    for t in terms:
        k = t.strip().lower()
        if k in common:
            continue
        if len(k) < 3:
            continue
        keep.append(k)

    seen = set()
    out = []
    for k in keep:
        if k not in seen:
            out.append(k)
            seen.add(k)
    return out[:60]

def extract_resume_claims(resume_text: str) -> List[str]:
    lines = [l.strip() for l in resume_text.splitlines()]
    bullets = [l for l in lines if l.startswith(("-", "•", "*")) and len(l) > 20]
    return bullets[:120]

def check_grounding(generated_points: List[str], resume_claims: List[str]) -> Dict[str, Any]:
    resume_blob = " ".join(resume_claims).lower()
    flagged = []
    for p in generated_points:
        p_l = p.lower()
        tokens = [t for t in re.findall(r"[a-z]{4,}", p_l)]
        overlap = sum(1 for t in set(tokens) if t in resume_blob)
        if overlap < 2:
            flagged.append({"point": p, "reason": "Low overlap with resume evidence"})
    return {
        "flagged": flagged,
        "ok_count": len(generated_points) - len(flagged),
        "flagged_count": len(flagged),
    }

async def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    if not TAVILY_API_KEY:
        return {"error": "Missing TAVILY_API_KEY", "query": query, "results": []}

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False,
            },
        )
        r.raise_for_status()
        data = r.json()

    results = [
        {"title": x.get("title"), "url": x.get("url"), "content": x.get("content")}
        for x in data.get("results", [])
    ]
    return {"query": query, "results": results}
