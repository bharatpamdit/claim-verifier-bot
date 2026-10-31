
# Claim Verifier Bot

An evidence-based GitHub Issue and Pull Request analysis tool that helps maintainers compare contributor claims with actual repository changes.

## Problem Statement

GitHub maintainers receive many issues and pull requests. Reviewing every claim manually takes time.

A contributor may claim that a feature has been implemented or that tests have been added, but the actual code changes may not provide sufficient supporting evidence.

Claim Verifier Bot helps maintainers inspect these claims using repository information and available code diffs.

## Features

- GitHub Issue and Pull Request URL validation.
- Repository metadata retrieval.
- Repository file listing.
- Fetch actual source files.
- Retrieve Pull Request changed files.
- Extract claims from PR titles and descriptions.
- Match claims against available code diffs.
- Identify claims with insufficient evidence.
- Generate an evidence-based report.
- REST API documentation through Swagger.
- Automated unit tests.

## Technology Stack

- Python
- FastAPI
- GitHub REST API
- HTTPX
- Pydantic
- Pytest

## Project Structure

```text
claim-verifier-bot/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env
│   └── venv/
│
├── frontend/
│
├── tests/
│   └── test_analysis.py
│
├── docs/
│   └── architecture.md
│
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/bharatpamdit/claim-verifier-bot.git
cd claim-verifier-bot
```

### 2. Create a virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure GitHub Token

Create a `.env` file inside the backend directory:

```env
GITHUB_TOKEN=your_github_personal_access_token
```

Never commit or share your GitHub token.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Backend runs at:

http://127.0.0.1:8000

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend welcome message |
| GET | `/health` | Health check |
| POST | `/fetch-source` | Fetch repository source file |
| POST | `/analyze` | Analyze GitHub Issue or PR |

## Analyze API Example

Endpoint:

```text
POST /analyze
```

Request:

```json
{
  "issue_url": "https://github.com/fastapi/fastapi/pull/1"
}
```

The response contains:

- Repository information
- Issue or Pull Request details
- Changed files
- Relevant files
- Claim analysis
- Evidence report

## Claim Analysis

The system extracts individual claims from a Pull Request title and description.

It compares extracted claim keywords with:

- Changed file paths
- Available Pull Request code diffs

Possible evidence statuses:

- `evidence_found`
- `insufficient_evidence`

These statuses indicate whether matching evidence was found. They do not establish that the claim is correct.

## Testing

Run tests from the backend directory:

```bash
PYTHONPATH=. pytest ../tests/test_analysis.py -v
```

The tests cover:

- Claim extraction
- Evidence matching
- Insufficient evidence detection
- Relevant file identification
- Evidence report generation

## Limitations

- Claim matching currently uses heuristic keyword matching.
- Semantic verification is not implemented.
- Automated test execution against contributor code is not performed.
- Some GitHub files may not provide patches.
- Evidence found does not guarantee correctness.
- Final decisions remain with repository maintainers.

## Future Improvements

- Semantic claim verification using AI/LLMs.
- Better code and documentation understanding.
- Test result integration through GitHub Actions.
- GitHub Webhooks for automatic PR analysis.
- Maintainer review dashboard.
- More advanced evidence confidence scoring.

## Project Goal

To assist open-source maintainers with evidence-based Issue and Pull Request triage while keeping final review decisions under human control.
