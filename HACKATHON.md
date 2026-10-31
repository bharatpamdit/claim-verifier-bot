Team Name: Phantom

Team Members:
    1. Rohan : rohan.s25383@nst.rishihood.edu.in
    2. Raj : toonu.s25479@nst.rishihood.edu.in
    3. Pankaj :pankak.k25317@nst.rishihood.edu.in
    4. Bharat : bharat.s25114@nst.rishihood.edu.in

PROBLEM 02: Evidence-Based Open Source Issue and Pull Request Triage



Problem Statement: Intelligent Technical Claim & Issue Verifier for Open-Source Repositories (or the specific AI / Open-Source Tooling / Gemma Track problem statement corresponding to automated issue/PR validation and code analysis from the hackathon list).

Summary: Building an intelligent GitHub App that automatically analyzes incoming GitHub issues and PRs, extracts verifiable technical claims, checks them against repository source code/docs, runs safe reproduction checks, and generates evidence-backed assessments for maintainers to combat invalid or hallucinated bug reports.

AI Models Being Used & Justification
1. Gemini 1.5 Pro / Gemini 2.0 (or Claude 3.5 Sonnet) AND others
Role: Primary Reasoning, Claim Extraction & Code Context Analysis

Justification: High-context window size allows the model to ingest large codebases, multi-file contexts, and extensive documentation simultaneously. It excels at complex reasoning—extracting discrete technical claims from issue descriptions and comparing them directly against the repository's source tree to identify hallucinations, invalid assumptions, or missing reproduction steps.

2. Gemma 2 (2B / 9B) or DeepSeek-Coder / CodeLlama (Open-Weight / Open-Source Model)
Role: Code Understanding, Log Parsing & Verification Synthesis

Justification: Satisfies the hackathon requirement for using open-source / open-weight models as a core component of the pipeline. It is light enough to run efficiently inside isolated CI/CD sandbox environments (e.g., Docker/GitHub Actions) to parse execution logs, evaluate stack traces, and summarize verification results without incurring external API overhead or exposing untrusted code.