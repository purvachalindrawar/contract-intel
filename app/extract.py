"""
Heuristic / lightweight extractor for common contract fields.
This is intentionally simple and deterministic (regex and keyword heuristics).
It returns JSON with fields requested by the assignment and evidence spans where possible.
"""

import re
from typing import Dict, Any, List

def _find_regex(text: str, pattern: str, flags=0):
    m = re.search(pattern, text, flags)
    if not m:
        return None
    return {"value": m.group(0).strip(), "start": m.start(), "end": m.end()}

def _find_keyword_sentence(text: str, keywords: List[str]):
    
    pattern = r"([^.?!\n]*?(?:%s)[^.?!\n]*[.?!\n])" % "|".join(re.escape(k) for k in keywords)
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return None
    return {"value": m.group(0).strip(), "start": m.start(), "end": m.end()}

def extract_fields(full_text: str) -> Dict[str, Any]:
    """
    Return dict with keys:
    parties, effective_date, term, governing_law, payment_terms, termination,
    auto_renewal (bool + evidence), confidentiality, indemnity, liability_cap,
    signatories (list)
    Each evidence includes 'value' and character span where found.
    """
    res: Dict[str, Any] = {}
    t = full_text or ""
    parties_patterns = [
        r"between\s+(.{1,200}?)\s+and\s+(.{1,200}?)\b",
        r"this\s+agreement\s+is\s+between\s+(.{1,200}?)\s+and\s+(.{1,200}?)\b",
    ]
    parties = []
    for p in parties_patterns:
        m = re.search(p, t, flags=re.IGNORECASE | re.DOTALL)
        if m:
            a = m.group(1).strip()
            b = m.group(2).strip()
            parties = [a, b]
            start = m.start()
            end = m.end()
            res["parties"] = {"value": parties, "start": start, "end": end}
            break
    if "parties" not in res:
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        candidates = []
        for ln in lines[:30]:  
            if re.search(r"\b(inc|ltd|llc|corporation|company|limited|co\.)\b", ln, flags=re.IGNORECASE):
                candidates.append(ln)
            if len(candidates) >= 2:
                break
        if candidates:
            res["parties"] = {"value": candidates, "start": 0, "end": 0}
    eff = _find_regex(t, r"effective\s+as\s+of\s+([A-Za-z0-9, \-]+)", flags=re.IGNORECASE)
    if not eff:
        eff = _find_regex(t, r"effective\s+date[:\s]*([A-Za-z0-9, \-]+)", flags=re.IGNORECASE)
    if not eff:
        eff = _find_regex(t, r"Effective\s*Date[:\s]*([A-Za-z0-9, \-]+)", flags=re.IGNORECASE)
    res["effective_date"] = eff
    term = _find_regex(t, r"term\s+of\s+([0-9]{1,2}\s+(?:year|years|month|months|day|days))", flags=re.IGNORECASE)
    if not term:
        term = _find_keyword_sentence(t, ["term of", "for a period of", "for a term of", "initial term"])
    res["term"] = term
    gov = _find_regex(t, r"governed\s+by\s+the\s+laws\s+of\s+([A-Za-z ,]+)", flags=re.IGNORECASE)
    res["governing_law"] = gov
    payment = _find_keyword_sentence(t, ["payment", "payable", "invoice", "fees"])
    res["payment_terms"] = payment

    termination = _find_keyword_sentence(t, ["termination", "terminate", "terminated"])
    res["termination"] = termination

    ar = _find_regex(t, r"(auto-?renew|automatically renew|renew automatically|automatic renewal)", flags=re.IGNORECASE)
    res["auto_renewal"] = ar is not None
    if ar:
        res["auto_renewal_evidence"] = {"value": ar["value"], "start": ar["start"], "end": ar["end"]}

    conf = _find_keyword_sentence(t, ["confidential", "confidentiality", "non-disclosure", "confidential information"])
    res["confidentiality"] = conf

    indemn = _find_keyword_sentence(t, ["indemnify", "indemnity", "hold harmless"])
    res["indemnity"] = indemn

    liab = _find_regex(t, r"(liabilit(?:y|ies).{0,80}?(?:cap|limited to|limited amount|not exceed|maximum))", flags=re.IGNORECASE)
    if not liab:
        liab = _find_regex(t, r"(no cap on liability|unlimited liability|liability not limited)", flags=re.IGNORECASE)
    res["liability_cap"] = liab

    sig = _find_regex(t, r"(Signed\s+by[:\s\S]{0,200}?)\n", flags=re.IGNORECASE)
    if not sig:
        sig = _find_keyword_sentence(t, ["Signature", "Signed", "Authorized Signature"])
    res["signatories"] = sig

    return res
