"""
Simple deterministic audit engine.
Each rule contains:
 - id, description, severity
 - regex pattern (case-insensitive)
When matched, we return a finding with start/end offsets and a short snippet.
"""

import re
from typing import List, Dict
RULES = [
    {
        "id": "auto_renewal_short_notice",
        "desc": "Auto-renewal with short notice",
        "severity": "high",
        "pattern": r"(auto-?renew|automatically renew|renewal.*?(?:notice|prior).*?(\d{1,2})\s?days)"
    },
    {
        "id": "unlimited_liability",
        "desc": "Unlimited liability or no liability cap",
        "severity": "critical",
        "pattern": r"(unlimited liability|no cap on liability|liability not limited|no limit on liability)"
    },
    {
        "id": "broad_indemnity",
        "desc": "Broad indemnity that may be risky",
        "severity": "medium",
        "pattern": r"(indemnif(?:y|ication)).{0,200}?(hold harmless|defend|indemnify)"
    },
    {
        "id": "confidentiality_exclusion",
        "desc": "Large exceptions to confidentiality",
        "severity": "medium",
        "pattern": r"(confidential).*?(not apply|except|exclusion|excepted)"
    }
]


def run_audit(full_text: str) -> List[Dict]:
    """
    Run the set of rules over the full_text (string).
    Return list of findings: {rule_id, description, severity, start, end, evidence}
    """
    findings = []
    if not full_text:
        return findings

    lower = full_text 
    for rule in RULES:
        try:
            match = re.search(rule["pattern"], lower, flags=re.IGNORECASE | re.DOTALL)
        except re.error:
            continue
        if match:
            start = match.start()
            end = match.end()
            ctx_start = max(0, start - 80)
            ctx_end = min(len(full_text), end + 80)
            snippet = full_text[ctx_start:ctx_end].strip()
            findings.append({
                "rule_id": rule["id"],
                "description": rule["desc"],
                "severity": rule["severity"],
                "start": start,
                "end": end,
                "evidence": snippet
            })
    return findings
