import base64
import re
import os
from urllib.parse import urlparse, quote

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl


# =====================================================
# CONFIGURATION
# =====================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


app = FastAPI(
    title="Claim Verifier Bot",
    description=(
        "Evidence-based GitHub Issue and Pull Request "
        "analysis with claim matching"
    ),
    version="2.0.0"
)


# =====================================================
# REQUEST MODELS
# =====================================================

class IssueRequest(BaseModel):
    issue_url: HttpUrl


class SourceFileRequest(BaseModel):
    repository_url: HttpUrl
    file_path: str
    branch: str = "main"


# =====================================================
# COMMON GITHUB API FUNCTION
# =====================================================

async def github_get(api_url, params=None):

    if not GITHUB_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="GITHUB_TOKEN missing. Check backend .env file."
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                api_url,
                headers=HEADERS,
                params=params
            )

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to GitHub: {str(error)}"
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=403,
            detail=(
                "GitHub API access forbidden. Check token permissions "
                "or API rate limit. " + response.text
            )
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="GitHub resource not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


# =====================================================
# FETCH REPOSITORY INFORMATION
# =====================================================

async def fetch_repository(owner, repo):

    api_url = f"{GITHUB_API}/repos/{owner}/{repo}"

    return await github_get(api_url)


# =====================================================
# FETCH REPOSITORY FILES
# =====================================================

async def fetch_repository_files(owner, repo, branch):

    api_url = (
        f"{GITHUB_API}/repos/{owner}/{repo}"
        f"/git/trees/{quote(branch, safe='')}?recursive=1"
    )

    data = await github_get(api_url)

    files = [
        item["path"]
        for item in data.get("tree", [])
        if item["type"] == "blob"
    ]

    return files


# =====================================================
# FETCH ACTUAL SOURCE CODE
# =====================================================

async def fetch_source_file(owner, repo, file_path, branch):

    encoded_path = quote(file_path, safe="/")

    api_url = (
        f"{GITHUB_API}/repos/{owner}/{repo}"
        f"/contents/{encoded_path}"
    )

    data = await github_get(
        api_url,
        params={"ref": branch}
    )

    if data.get("encoding") != "base64":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file encoding"
        )

    try:
        content = base64.b64decode(
            data["content"]
        ).decode("utf-8")

    except (ValueError, UnicodeDecodeError, KeyError):
        raise HTTPException(
            status_code=400,
            detail="Unable to decode source file"
        )

    return content


# =====================================================
# FETCH PULL REQUEST CHANGED FILES
# =====================================================

async def fetch_pull_request_files(owner, repo, pr_number):

    changed_files = []

    # Maximum 3 pages, 100 files per page.

    for page in range(1, 4):

        api_url = (
            f"{GITHUB_API}/repos/{owner}/{repo}"
            f"/pulls/{pr_number}/files"
        )

        data = await github_get(
            api_url,
            params={
                "per_page": 100,
                "page": page
            }
        )

        if not data:
            break

        for item in data:

            patch = item.get("patch")

            changed_files.append({
                "filename": item["filename"],
                "status": item["status"],
                "additions": item["additions"],
                "deletions": item["deletions"],
                "changes": item["changes"],
                "patch_available": patch is not None,
                "patch": patch[:5000] if patch else None,
                "patch_note": (
                    None if patch is not None
                    else "GitHub did not provide a patch for this file."
                )
            })

        if len(data) < 100:
            break

    return changed_files


# =====================================================
# TEXT PROCESSING HELPERS
# =====================================================

STOP_WORDS = {
    "the", "is", "are", "a", "an", "and", "or",
    "to", "in", "of", "for", "with", "when",
    "this", "that", "it", "on", "from", "by",
    "as", "at", "be", "been", "being", "was",
    "were", "have", "has", "had", "do", "does",
    "did", "will", "would", "should", "could",
    "can", "may", "might", "we", "i", "you",
    "they", "them", "their", "our", "my",
    "both", "also", "into", "using", "use",
    "added", "add", "new", "support", "supports",
    "test", "tests", "testing", "tested",
    "please", "issue", "pull", "request",
    "fix", "bug", "change", "changes",
    "update", "updated", "make", "made",
    "these", "those", "which", "what",
    "include", "includes", "including",
    "following", "following", "such",
    "path", "paths", "endpoint", "endpoints"
}


def normalize_words(text):

    # Treat underscores as word separators
    text = text.replace("_", " ")

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9]*",
        text.lower()
    )

    normalized = set()

    for word in words:

        if word.endswith("s") and len(word) > 4:
            word = word[:-1]

        if word not in STOP_WORDS and len(word) > 1:
            normalized.add(word)

    return normalized


# =====================================================
# EXTRACT CLAIMS FROM PR DESCRIPTION
# =====================================================

def extract_claims(title, description):

    text = (title or "") + "\n" + (description or "")

    # Split text into individual sentences / bullet points.

    parts = re.split(
        r"[\n.!?;]+",
        text
    )

    claims = []
    seen = set()

    for part in parts:

        claim = re.sub(
            r"^\s*[-*•\d.)]+\s*",
            "",
            part
        ).strip()

        if not claim:
            continue

        # Avoid duplicate claims.

        key = claim.lower()

        if key not in seen:

            seen.add(key)

            claims.append({
                "claim": claim
            })

    return claims[:20]


# =====================================================
# MATCH CLAIMS AGAINST ACTUAL PR DIFFS
# =====================================================

def match_claims_with_evidence(claims, changed_files):

    claim_results = []

    for claim_data in claims:

        claim_text = claim_data["claim"]

        claim_keywords = normalize_words(claim_text)

        matched_files = []
        all_matched_keywords = set()

        for file_data in changed_files:

            filename = file_data["filename"]
            patch = file_data.get("patch") or ""

            # Match against filename AND actual code diff.

            evidence_text = filename + " " + patch

            evidence_keywords = normalize_words(evidence_text)

            matched_keywords = (
                claim_keywords & evidence_keywords
            )

            if matched_keywords:

                matched_files.append({
                    "file": filename,
                    "matched_keywords": sorted(matched_keywords),
                    "patch_available": file_data["patch_available"]
                })

                all_matched_keywords.update(
                    matched_keywords
                )

        if matched_files:

            status = "evidence_found"

            explanation = (
                "Supporting keywords were found in the changed "
                "file paths or available code diffs. "
                "Manual review is still required."
            )

        else:

            status = "insufficient_evidence"

            explanation = (
                "No matching keywords were found in the available "
                "PR diffs. This does not prove the claim is false."
            )

        claim_results.append({

            "claim": claim_text,

            "evidence_status": status,

            "matched_files": matched_files,

            "matched_keywords": sorted(
                all_matched_keywords
            ),

            "explanation": explanation
        })

    evidence_count = sum(
        1 for item in claim_results
        if item["evidence_status"] == "evidence_found"
    )

    return {
        "total_claims": len(claim_results),
        "claims_with_evidence": evidence_count,
        "claims_without_sufficient_evidence": (
            len(claim_results) - evidence_count
        ),
        "claims": claim_results,
        "method": (
            "Heuristic keyword matching against PR file paths "
            "and available code diffs"
        ),
        "warning": (
            "Evidence found is not proof of correctness. "
            "The bot does not execute code or run tests."
        )
    }


# =====================================================
# RELEVANT FILE IDENTIFICATION FOR ISSUES
# =====================================================

def find_relevant_files(issue_text, files):

    keywords = normalize_words(issue_text)

    results = []

    for file in files:

        file_words = normalize_words(file)

        matched_keywords = keywords & file_words

        score = len(matched_keywords)

        if score > 0:

            results.append({
                "file": file,
                "score": score,
                "matched_keywords": sorted(matched_keywords),
                "reason": "Filename/path keyword match"
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:10]


# =====================================================
# EVIDENCE REPORT
# =====================================================

def create_evidence_report(
    issue_type,
    changed_files,
    relevant_files,
    claim_analysis=None
):

    if issue_type == "pull_request":

        total = len(changed_files)

        patch_count = sum(
            1 for file in changed_files
            if file["patch_available"]
        )

        return {
            "status": "needs_maintainer_review",

            "total_changed_files": total,

            "files_with_patch": patch_count,

            "files_without_patch": total - patch_count,

            "total_claims": (
                claim_analysis["total_claims"]
                if claim_analysis else 0
            ),

            "claims_with_evidence": (
                claim_analysis["claims_with_evidence"]
                if claim_analysis else 0
            ),

            "claims_without_sufficient_evidence": (
                claim_analysis["claims_without_sufficient_evidence"]
                if claim_analysis else 0
            ),

            "evidence_source": (
                "GitHub Pull Request Files API and "
                "heuristic claim-to-diff matching"
            ),

            "summary": (
                "PR changes and available code diffs were collected. "
                "Claims were compared with the available evidence. "
                "Maintainer review is still required."
            ),

            "limitations": [
                "Some files may not have a patch.",
                "Claim matching is based on keywords, not deep semantic understanding.",
                "No automated tests have been executed.",
                "The bot does not prove that a claim is correct.",
                "A maintainer must review the changes."
            ]
        }

    return {
        "status": "insufficient_evidence",

        "suggested_files": len(relevant_files),

        "evidence_source": "Filename/path keyword matching",

        "summary": (
            "Potentially relevant repository files were suggested. "
            "The issue claim has not been verified."
        ),

        "limitations": [
            "Filename matching can produce false positives.",
            "Source code has not been semantically inspected.",
            "No automated tests have been executed.",
            "A maintainer must verify the issue."
        ]
    }


# =====================================================
# HOME ROUTE
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Claim Verifier Bot Backend is Running!",
        "version": "2.0.0"
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =====================================================
# FETCH SOURCE API
# =====================================================

@app.post("/fetch-source")
async def get_source_code(request: SourceFileRequest):

    parsed_url = urlparse(
        str(request.repository_url)
    )

    if parsed_url.hostname != "github.com":
        raise HTTPException(
            status_code=400,
            detail="Only GitHub repository URLs are supported"
        )

    parts = parsed_url.path.strip("/").split("/")

    if len(parts) < 2:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL"
        )

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    content = await fetch_source_file(
        owner,
        repo,
        request.file_path,
        request.branch
    )

    return {
        "repository": repo,
        "file_path": request.file_path,
        "source_code": content
    }


# =====================================================
# MAIN ISSUE / PR ANALYSIS API
# =====================================================

@app.post("/analyze")
async def analyze_issue(request: IssueRequest):

    url = str(request.issue_url)

    parsed_url = urlparse(url)

    if parsed_url.hostname != "github.com":
        raise HTTPException(
            status_code=400,
            detail="Only GitHub URLs are supported"
        )

    parts = parsed_url.path.strip("/").split("/")

    if len(parts) != 4 or parts[2] not in ["issues", "pull"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub Issue or PR URL"
        )

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    issue_number = parts[3]

    if not issue_number.isdigit():

        raise HTTPException(
            status_code=400,
            detail="Invalid issue or PR number"
        )

    # STEP 1: Fetch Issue / PR data.

    api_url = (
        f"{GITHUB_API}/repos/{owner}/{repo}"
        f"/issues/{issue_number}"
    )

    issue_data = await github_get(api_url)

    # STEP 2: Identify actual type.

    issue_type = (
        "pull_request"
        if "pull_request" in issue_data
        else "issue"
    )

    # STEP 3: Fetch repository information.

    repo_data = await fetch_repository(
        owner,
        repo
    )

    # STEP 4: Fetch repository files.

    files = await fetch_repository_files(
        owner,
        repo,
        repo_data["default_branch"]
    )

    # STEP 5: Prepare Issue / PR text.

    title = issue_data.get("title") or ""
    description = issue_data.get("body") or ""

    issue_text = title + " " + description

    changed_files = []
    relevant_files = []
    claim_analysis = None

    # STEP 6: PR analysis.

    if issue_type == "pull_request":

        changed_files = await fetch_pull_request_files(
            owner,
            repo,
            issue_number
        )

        # Extract claims from PR title and description.

        claims = extract_claims(
            title,
            description
        )

        # Match each claim against actual PR diffs.

        claim_analysis = match_claims_with_evidence(
            claims,
            changed_files
        )

    # STEP 7: Issue analysis.

    else:

        relevant_files = find_relevant_files(
            issue_text,
            files
        )

    # STEP 8: Create evidence report.

    evidence_report = create_evidence_report(
        issue_type,
        changed_files,
        relevant_files,
        claim_analysis
    )

    # STEP 9: Final response.

    return {

        "repository": {
            "name": repo_data["name"],
            "description": repo_data["description"],
            "language": repo_data["language"],
            "default_branch": repo_data["default_branch"],
            "stars": repo_data["stargazers_count"],
            "total_files": len(files),
            "files": files[:30]
        },

        "issue": {
            "type": issue_type,
            "number": issue_number,
            "title": title,
            "description": description,
            "state": issue_data.get("state"),
            "url": issue_data.get("html_url")
        },

        "changed_files": changed_files,

        "relevant_files": relevant_files,

        "claim_analysis": claim_analysis,

        "evidence_report": evidence_report
    }