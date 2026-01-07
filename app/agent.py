import os
import json
from typing import Any, Dict, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

from app.prompts import SYSTEM
from app import tools as tool_impl

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4.1-mini")

TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "create_action_plan",
            "description": "Create a JSON action plan (steps) for the agent to execute.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": ["string","null"]},
                    "role_title": {"type": ["string","null"]},
                    "job_url": {"type": ["string","null"]},
                },
                "required": ["company_name","role_title","job_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": "Extract ATS-style keywords from job text.",
            "parameters": {
                "type": "object",
                "properties": {"job_text": {"type": "string"}},
                "required": ["job_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_resume_claims",
            "description": "Extract bullet-like evidence lines from resume text.",
            "parameters": {
                "type": "object",
                "properties": {"resume_text": {"type": "string"}},
                "required": ["resume_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_grounding",
            "description": "Flag generated bullets that are weakly supported by resume evidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "generated_points": {"type": "array", "items": {"type": "string"}},
                    "resume_claims": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["generated_points", "resume_claims"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for company/news/context and return top results with snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
]

async def _run_tool(name: str, args: Dict[str, Any]) -> Any:
    if name == "create_action_plan":
        return tool_impl.create_action_plan(**args)
    if name == "extract_keywords":
        return tool_impl.extract_keywords(**args)
    if name == "extract_resume_claims":
        return tool_impl.extract_resume_claims(**args)
    if name == "check_grounding":
        return tool_impl.check_grounding(**args)
    if name == "web_search":
        return await tool_impl.web_search(**args)
    raise ValueError(f"Unknown tool: {name}")

def _safe_get_text(response) -> str:
    final_text = ""
    for o in response.output:
        if o.type == "message":
            final_text += o.content[0].text
    return final_text

def _ensure_keys(base: Dict[str, Any]) -> Dict[str, Any]:
    base.setdefault("jd_summary", {})
    base.setdefault("ats_keywords", [])
    base.setdefault("company_research", {"overview": "", "recent_news": []})
    base.setdefault("tailored_resume_bullets", [])
    base.setdefault("cover_letter", "")
    base.setdefault("interview_pack", {"star_stories": [], "behavioral_qs": [], "technical_qs": []})
    base.setdefault("verifier_report", {})
    return base

async def _llm_step(step_id: str, step_name: str, working: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Ask the model to produce a JSON patch for the working output."""
    prompt = {
        "step_id": step_id,
        "step_name": step_name,
        "context": context,
        "working_output_so_far": working,
    }

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"""Perform ONLY this step and return a JSON PATCH object (only keys you update).
Do not include markdown. Do not include extra text.

Step:
{json.dumps(prompt)}

Rules:
- Do NOT invent anything not supported by resume_text.
- If data is missing, write a neutral version.
- Use existing extracted keywords / research already present in working_output_so_far when possible.

Expected patch keys depend on the step:
- S4 -> jd_summary
- S5 -> tailored_resume_bullets
- S7 -> cover_letter
- S8 -> interview_pack
- S9 -> verifier_report
"""}
        ],
        tools=TOOL_DEFS,
        tool_choice="none",
    )

    patch_text = _safe_get_text(response)
    return json.loads(patch_text)

async def run_copilot(job_text: str, resume_text: str, company_name: Optional[str], role_title: Optional[str], job_url: Optional[str]) -> Dict[str, Any]:
    # ----- State machine -----
    plan = tool_impl.create_action_plan(company_name=company_name, role_title=role_title, job_url=job_url)
    steps: List[Dict[str, Any]] = plan["steps"]

    working: Dict[str, Any] = _ensure_keys({})
    execution_log: Dict[str, Any] = {
        "plan_id": plan["plan_id"],
        "steps": [],
    }

    context = {
        "job_url": job_url,
        "company_name": company_name,
        "role_title": role_title,
        "job_text": job_text,
        "resume_text": resume_text,
    }

    # Step outputs we may want to keep around
    resume_claims: List[str] = []
    keywords: List[str] = []
    research_results: Dict[str, Any] = {}

    for step in steps:
        sid = step["id"]
        name = step["name"]
        kind = step["kind"]
        tool = step.get("tool")

        log_entry = {"id": sid, "name": name, "kind": kind, "status": "pending"}

        try:
            if kind == "tool":
                if tool == "extract_keywords":
                    keywords = tool_impl.extract_keywords(job_text=job_text)
                    working["ats_keywords"] = keywords

                    log_entry["status"] = "done"
                    log_entry["output_summary"] = {"keyword_count": len(keywords)}

                elif tool == "extract_resume_claims":
                    resume_claims = tool_impl.extract_resume_claims(resume_text=resume_text)
                    log_entry["status"] = "done"
                    log_entry["output_summary"] = {"resume_claims_count": len(resume_claims)}

                elif tool == "web_search":
                    if not company_name:
                        log_entry["status"] = "skipped"
                        log_entry["reason"] = "company_name missing"
                    else:
                        # gather 2-3 searches
                        q1 = f"{company_name} engineering blog"
                        q2 = f"{company_name} recent news"
                        q3 = f"{company_name} {role_title or ''} tech stack".strip()

                        r1 = await tool_impl.web_search(query=q1, max_results=4)
                        r2 = await tool_impl.web_search(query=q2, max_results=4)
                        r3 = await tool_impl.web_search(query=q3, max_results=4)

                        research_results = {"engineering_blog": r1, "recent_news": r2, "role_stack": r3}

                        # create a compact company_research object (overview left for LLM to write)
                        news_items = []
                        for x in (r2.get("results") or [])[:4]:
                            if x.get("title") and x.get("url"):
                                news_items.append({"title": x["title"], "url": x["url"]})

                        working["company_research"] = {"overview": "", "recent_news": news_items}
                        log_entry["status"] = "done"
                        log_entry["output_summary"] = {"news_items": len(news_items), "has_error": bool(r2.get("error"))}

                elif tool == "check_grounding":
                    # run grounding check on current bullets; then fix with LLM if needed
                    bullets = working.get("tailored_resume_bullets", [])
                    report = tool_impl.check_grounding(generated_points=bullets, resume_claims=resume_claims)
                    # if flagged, ask LLM to rewrite only flagged bullets
                    if report.get("flagged_count", 0) > 0:
                        flagged_points = [f["point"] for f in report["flagged"]]
                        response = client.responses.create(
                            model=MODEL,
                            input=[
                                {"role": "system", "content": SYSTEM},
                                {"role": "user", "content": json.dumps({
                                    "task": "Rewrite ONLY the flagged bullets to be grounded in resume evidence or neutral.",
                                    "job_text": job_text,
                                    "ats_keywords": keywords,
                                    "resume_claims": resume_claims,
                                    "flagged_points": flagged_points,
                                    "rules": [
                                        "Do not invent metrics or tools not in resume",
                                        "Keep bullets ATS dense",
                                        "Return JSON: {rewrites: [{from:..., to:...}]}"
                                    ]
                                })}
                            ],
                            tools=TOOL_DEFS,
                            tool_choice="none",
                        )
                        rewrites = json.loads(_safe_get_text(response)).get("rewrites", [])
                        # apply rewrites
                        new_bullets = []
                        for b in bullets:
                            replaced = False
                            for rw in rewrites:
                                if rw.get("from") == b and rw.get("to"):
                                    new_bullets.append(rw["to"])
                                    replaced = True
                                    break
                            if not replaced:
                                new_bullets.append(b)
                        working["tailored_resume_bullets"] = new_bullets
                        # rerun report after rewrite
                        report = tool_impl.check_grounding(generated_points=new_bullets, resume_claims=resume_claims)

                    working["verifier_report"] = working.get("verifier_report", {})
                    working["verifier_report"]["grounding_check"] = report
                    log_entry["status"] = "done"
                    log_entry["output_summary"] = {"flagged_count": report.get("flagged_count", 0)}

                else:
                    raise ValueError(f"Unhandled tool step: {tool}")

            else:
                # LLM steps (S4/S5/S7/S8/S9)
                patch = await _llm_step(sid, name, working, {
                    **context,
                    "ats_keywords": keywords,
                    "resume_claims": resume_claims,
                    "research_results": research_results,
                })
                # merge patch
                for k, v in patch.items():
                    working[k] = v

                # Special: if company overview is empty but we have research, fill it quickly in S4 or S7 pass.
                if working.get("company_research") and not working["company_research"].get("overview") and company_name:
                    # allow LLM to write a 2-3 sentence overview from research snippets
                    response = client.responses.create(
                        model=MODEL,
                        input=[
                            {"role": "system", "content": SYSTEM},
                            {"role": "user", "content": json.dumps({
                                "task": "Write a short company overview (2-3 sentences) based only on provided search snippets. If missing, write neutral.",
                                "company_name": company_name,
                                "snippets": {
                                    "engineering_blog": (research_results.get("engineering_blog", {}).get("results", [])[:2] if research_results else []),
                                    "recent_news": (research_results.get("recent_news", {}).get("results", [])[:2] if research_results else []),
                                },
                                "output_format": {"overview": "string"}
                            })}
                        ],
                        tool_choice="none",
                    )
                    ov = json.loads(_safe_get_text(response)).get("overview", "")
                    working["company_research"]["overview"] = ov

                log_entry["status"] = "done"
                log_entry["output_summary"] = {"patched_keys": list(patch.keys())}

        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)

        execution_log["steps"].append(log_entry)

    # Ensure all required keys exist
    working = _ensure_keys(working)
    working["execution_log"] = execution_log
    return working
