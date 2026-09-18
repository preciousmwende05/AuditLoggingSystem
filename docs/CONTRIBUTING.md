# Contributing and Git Workflow

This document defines how this project is developed sprint over sprint. It exists so that even a solo fourth year project is graded on visible, professional process, not just a final zip file.

## Branch strategy

- `main` always reflects a working, demoable state. Nothing broken is merged here.
- `develop` is the integration branch for the current sprint. Feature work branches off `develop` and merges back into it.
- Feature branches are named `feature/<short-description>`, for example `feature/audit-log-hash-chain`.
- Bug fix branches are named `fix/<short-description>`.
- At the end of each sprint, `develop` is merged into `main` and tagged, for example `v0.1.0-sprint1`.

## Commit message convention

This project follows Conventional Commits so the history itself documents what happened sprint by sprint:

```
feat: add hash chaining to audit log service
fix: correct sequence ordering in chain verification
docs: add sprint 1 setup instructions
chore: configure pre-commit hooks
test: add chain tamper detection test
```

Prefixes used: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`.

## Pull requests (even solo)

Even working alone, feature branches are opened as pull requests into `develop` before merging, using GitHub's compare view, so that:

1. CI (GitHub Actions) runs lint and tests automatically before merge.
2. There is a reviewable diff and a written rationale per change, useful evidence for supervisors reviewing project process.

## Local setup for contributing

1. Install pre-commit hooks once per clone:

   ```
   pip install pre-commit
   pre-commit install
   ```

2. Hooks run automatically on `git commit` and will auto-fix formatting where possible (black, isort, ruff --fix, trailing whitespace).

## Sprint tracking

Each sprint's deliverables and status are tracked in `docs/sprints/`. Create one file per sprint, for example `docs/sprints/sprint-1.md`, and check items off as they are completed so progress is visible in the repository itself, not only in conversation.
