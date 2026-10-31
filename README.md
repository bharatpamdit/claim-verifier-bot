# IssueLens AI
**Don't Trust Claims. Verify Them With Code.**

A runnable hackathon MVP: connect a public GitHub repository, fetch open issues, extract technical claims using a local Ollama model, search JS/Python files for candidate evidence, and show a cautious triage report.

## Requirements
- Node.js 20+
- Python 3.10+
- Ollama installed locally

## Run
### 1) Pull and start a local model
```bash
ollama pull qwen2.5-coder:3b
ollama serve
```
If Ollama already runs in the background, just pull the model.

### 2) Start the analyzer
```bash
cd analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

### 3) Start the API
```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

### 4) Start the UI
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Features in this MVP
- Public GitHub URL validation and repository metadata
- Whole-repository report with file inventory, language totals, dependency/build manifests, entry-point hints, README excerpt, and static project-health signals
- Fetch open issues and PRs
- Local Ollama claim extraction and evidence assessment
- Python AST symbol discovery and JS/Python keyword evidence search
- Evidence file path, line range and snippets
- Verdicts: Confirmed, Invalid, Cannot Reproduce, Uncertain

## Important limitations
This MVP uses static code search; it does not execute contributor code or run repository tests. Static matches are candidate evidence, not proof. If reproduction evidence is missing, prefer Uncertain. No comments, labels, issues or PRs are posted to real repositories. Analysis results are held in memory and disappear when the backend restarts. This is a starter implementation, not a production security-reviewed GitHub App.

## Configuration
`backend/.env`:
```env
PORT=5001
ANALYZER_URL=http://127.0.0.1:8001
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5-coder:3b
GITHUB_TOKEN=
```
A GitHub token is optional for public repos but required once the anonymous IP rate limit is reached. The UI has a password field for a token; it is held in page memory and sent only to the local backend. For public repos, create a fine-grained personal access token with read-only access to repository metadata, issues, and contents. Never commit or share the token. Source files are fetched from raw.githubusercontent.com after the GitHub tree request to reduce API rate-limit use.

## Four-person split
1. Backend/GitHub API
2. Ollama/claim extraction and assessment
3. Python + JS analyzer/evidence
4. React UI and integration

Before hackathon submission, complete `HACKATHON.md`, verify organizer-required first-commit rules, add actual tested examples, and ensure CI passes.
