from app.main import (
    extract_claims,
    match_claims_with_evidence,
    find_relevant_files,
    create_evidence_report
)


def test_extract_claims():

    claims = extract_claims(
        "Add path tests",
        "Added min_length tests.\nAdded max_length tests."
    )

    assert len(claims) == 3
    assert claims[0]["claim"] == "Add path tests"


def test_claim_evidence_found():

    claims = [
        {"claim": "Tests cover min_length and max_length"}
    ]

    changed_files = [
        {
            "filename": "tests/test_path.py",
            "patch": "+ test_min_length and test_max_length",
            "patch_available": True
        }
    ]

    result = match_claims_with_evidence(
        claims,
        changed_files
    )

    assert result["claims_with_evidence"] == 1
    assert result["claims"][0]["evidence_status"] == "evidence_found"


def test_claim_insufficient_evidence():

    claims = [
        {"claim": "Database migration was completed"}
    ]

    changed_files = [
        {
            "filename": "tests/test_path.py",
            "patch": "+ test_min_length",
            "patch_available": True
        }
    ]

    result = match_claims_with_evidence(
        claims,
        changed_files
    )

    assert result["claims_without_sufficient_evidence"] == 1


def test_find_relevant_files():

    files = [
        "app/authentication.py",
        "tests/test_payment.py",
        "README.md"
    ]

    result = find_relevant_files(
        "authentication bug",
        files
    )

    assert len(result) > 0
    assert result[0]["file"] == "app/authentication.py"


def test_evidence_report():

    result = create_evidence_report(
        "pull_request",
        [
            {
                "patch_available": True
            },
            {
                "patch_available": False
            }
        ],
        [],
        {
            "total_claims": 2,
            "claims_with_evidence": 1,
            "claims_without_sufficient_evidence": 1
        }
    )

    assert result["total_changed_files"] == 2
    assert result["files_with_patch"] == 1
    assert result["claims_with_evidence"] == 1
    assert result["status"] == "needs_maintainer_review"