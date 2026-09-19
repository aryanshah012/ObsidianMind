# Contributing to ObsidianMind

Thanks for your interest in improving **ObsidianMind**.

## Development Workflow

1. Fork or clone the repository.
2. Create a focused branch such as `feat/short-description` or `fix/short-description`.
3. Make a small, reviewable change.
4. Run the project checks locally.
5. Use a clear commit message, preferably following Conventional Commits.
6. Open a pull request explaining the problem, approach, testing, and any trade-offs.

## Local Setup

Python:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm ci
```

## Before Opening a Pull Request

Run:
```bash
pytest tests -q
cd frontend && npm run lint && npm run build
```

RAG or retrieval changes should include evidence that citations, fallback behavior, and grounding still work as expected.

## Commit Style

Examples:

```text
feat: add verified risk decision trace
fix: prevent duplicate recovery actions
test: cover retrieval fallback behavior
docs: clarify local setup
refactor: isolate policy evaluation
```

## Pull Request Expectations

A strong pull request should include:

- what changed and why
- screenshots for meaningful UI changes
- tests or validation steps
- any migration or environment changes
- security or safety implications, if relevant

Please keep unrelated changes out of the same pull request so reviews stay fast and focused.
