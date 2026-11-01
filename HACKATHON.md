# Hackathon Declaration

<<<<<<< HEAD
- Team name: [ADD TEAM NAME]
- Members: [MEMBER 1], [MEMBER 2], [MEMBER 3], [MEMBER 4]
- Selected problem: Problem 02 — Evidence-Based Open Source Issue and Pull Request Triage
- Project: IssueLens AI
- AI model: Qwen2.5-Coder through Ollama (local inference)
- Reason: Code-oriented open-weight model for extracting technical claims and explaining supplied code evidence. Model size is chosen based on machine memory and tested locally.
- Core AI inference runs locally. GitHub API is used to retrieve public repository data.
=======
- Team name: Phantom
- Members: Rohan, Raj, Pankaj, and Bharat (team details from the original repository submission)
- Selected problem: Problem 02 — Evidence-Based Open Source Issue and Pull Request Triage
- Project: Claim Verifier Bot / IssueLens AI
- AI model: Qwen2.5-Coder through Ollama (local inference)
- Reason: A code-oriented open-weight model extracts technical claims and explains candidate evidence from the supplied repository. Inference runs locally; repository data is fetched through GitHub's public API.

## Implemented scope

The current MVP fetches public issues and pull requests, extracts claims, searches source code and documentation for candidate evidence, and presents cautious findings. Static matches are not proof, and the tool does not execute untrusted contributor code or post comments, labels, or other changes to GitHub.
>>>>>>> 490d8ccd215d7cdce28052666cc209fdd8f0c39f
