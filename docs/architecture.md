
# System Architecture

## Overview

Claim Verifier Bot uses a Python FastAPI backend to communicate with the GitHub REST API and analyze repository issues and pull requests.

## Workflow

1. User submits a GitHub Issue or PR URL.
2. Backend validates the URL.
3. Backend retrieves Issue/PR information from GitHub.
4. Repository metadata and file information are retrieved.
5. If the URL refers to a PR:
   - Fetch changed files.
   - Retrieve available code diffs.
   - Extract claims from the title and description.
   - Match claims against available diffs.
6. If the URL refers to an Issue:
   - Extract keywords from its title and description.
   - Identify potentially relevant repository files.
7. Generate an evidence report.
8. Return the analysis as JSON.

## Main Components

### FastAPI
Provides HTTP endpoints and handles incoming requests.

### GitHub REST API
Provides repository information, issue details, source files and pull request diffs.

### Claim Extraction
Splits PR text into individual statements for analysis.

### Evidence Matching
Uses keyword matching to identify supporting terms in changed file paths and available diffs.

### Evidence Report
Summarizes collected evidence and highlights limitations for maintainers.

## Human-in-the-Loop

The system does not automatically approve or reject pull requests.

It provides evidence to support human review. Maintainers remain responsible for final decisions.

## Security Considerations

- GitHub tokens are stored in environment variables.
- Secrets must not be committed to Git.
- Contributor code is not executed by the analyzer.
- API access is performed through authenticated GitHub requests.
