# Agent Rules

## This agent may:
- Create feature branches (prefix: `ai/` or `agent/`)
- Commit and push to its own feature branches
- Open pull requests for human review
- Read all files in this repository

## This agent must NOT:
- Push directly to `main` or `develop`
- Modify `.env` files or any file containing secrets
- Modify `.github/workflows/` (CI/CD pipelines)
- Modify this file (AGENT_RULES.md)
- Delete any branch other than its own feature branches
