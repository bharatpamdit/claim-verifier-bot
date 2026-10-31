from app import analyze, Request

def test_analyzer_returns_candidate_evidence():
    req=Request(claims=[{"id":"c1","claim":"token validation","keywords":["token","validation"]}],
                files=[{"path":"auth.py","content":"def validate_token(token):\n    return token is not None\n"}])
    result=analyze(req)
    assert result["evidence"][0]["evidenceCount"] > 0

def test_no_match_is_not_a_verdict():
    req=Request(claims=[{"id":"c1","claim":"payment timeout","keywords":["payment","timeout"]}],
                files=[{"path":"x.py","content":"print('hello')"}])
    result=analyze(req)
    assert result["evidence"][0]["status"] == "no_candidate_evidence_found"
