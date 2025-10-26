# app/tests/test_audit.py
from app.audit import run_audit

def test_run_audit_empty():
    findings = run_audit("")
    assert isinstance(findings, list)
    assert findings == []

def test_run_audit_sample():
    txt = "This agreement will automatically renew and includes unlimited liability for party."
    findings = run_audit(txt)
    # Expect at least two findings: auto-renewal and unlimited liability
    ids = {f["rule_id"] for f in findings}
    assert "auto_renewal_short_notice" in ids or "auto_renewal_short_notice" in ids
    assert "unlimited_liability" in ids
