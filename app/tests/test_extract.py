# app/tests/test_extract.py
from app.extract import extract_fields

def test_extract_empty():
    r = extract_fields("")
    assert isinstance(r, dict)
    # keys exist
    expected_keys = ["parties","effective_date","term","governing_law","payment_terms","termination","auto_renewal","confidentiality","indemnity","liability_cap","signatories"]
    for k in expected_keys:
        assert k in r

def test_extract_sample_text():
    txt = "This Agreement is between Alpha Inc and Beta LLC. Effective Date: January 1, 2024. The term is for a period of 2 years."
    r = extract_fields(txt)
    assert r["parties"] is not None
    assert r["effective_date"] is not None
    assert r["term"] is not None
