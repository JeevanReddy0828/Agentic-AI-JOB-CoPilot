import re
from typing import List, Dict

def ats_score(job_keywords: List[str], resume_text: str) -> Dict:
    r = resume_text.lower()
    hits, misses = [], []

    for k in job_keywords:
        k2 = (k or "").strip().lower()
        if not k2:
            continue
        pattern = r"\b" + re.escape(k2) + r"\b"
        if re.search(pattern, r):
            hits.append(k)
        else:
            misses.append(k)

    coverage = len(hits) / max(1, len(job_keywords))
    score = round(100 * coverage)

    return {
        "score": score,
        "coverage": round(coverage, 3),
        "hit_count": len(hits),
        "miss_count": len(misses),
        "hits": hits[:50],
        "misses": misses[:50],
    }
