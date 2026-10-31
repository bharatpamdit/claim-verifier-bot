import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
import re

async def fetch_repository(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Unable to fetch repository"
        )

    return response.json()
async def fetch_repository_files(owner, repo, branch):

    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Unable to fetch repository files"
        )

    data = response.json()

    files = [
        item["path"]
        for item in data["tree"]
        if item["type"] == "blob"
    ]

    return files
async def fetch_source_file(owner, repo, file_path, branch):

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            params={"ref": branch},
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Source file not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
    )

    data = response.json()

    if data.get("encoding") != "base64":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file encoding"
        )

    content = base64.b64decode(data["content"]).decode("utf-8")

    return content

app = FastAPI(
    title="Claim Verifier Bot",
    description="Evidence-based GitHub Issue and PR verification",
    version="1.0.0"
)


class IssueRequest(BaseModel):
    issue_url: HttpUrl

class SourceFileRequest(BaseModel):
    repository_url: HttpUrl
    file_path: str
    branch: str = "main"
@app.get("/")
def home():
    return {
        "message": "Claim Verifier Bot Backend is Running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
@app.post("/fetch-source")
async def get_source_code(request: SourceFileRequest):

    url = str(request.repository_url)

    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)

    if not match:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL"
        )

    owner, repo = match.groups()

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
async def analyze_issue(request: IssueRequest):

    url = str(request.issue_url)

    # Extract owner, repository and issue number
    pattern = r"github\.com/([^/]+)/([^/]+)/issues/(\d+)"
    match = re.search(pattern, url)

    if not match:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub Issue URL"
        )

    owner, repo, issue_number = match.groups()

    # GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers={
                "Accept": "application/vnd.github+json"
            }
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="GitHub issue or repository not found"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Unable to fetch GitHub issue"
        )

    issue_data = response.json()
    repo_data = await fetch_repository(owner, repo)
    files = await fetch_repository_files(
    owner,
    repo,
    repo_data["default_branch"]
)

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
        "number": issue_number,
        "title": issue_data["title"],
        "description": issue_data["body"],
        "state": issue_data["state"],
        "url": issue_data["html_url"]
    }
}