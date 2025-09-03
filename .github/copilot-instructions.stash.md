<!-- Generated with Claude Sonnet 4 - 2025-09-03 - Automated checkpointing recommendations using git stash -->

```instructions
<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions (stash-autocheckpoint)

This file is a companion to `.github/copilot-instructions.md`. It uses that file as a baseline and adds focused recommendations for automated agent-created checkpoints using `git stash` semantics. The intent is to give a safe, non-destructive workflow so Copilot/agent updates are auditable and recoverable prior to any remote commit.

## Model Preference
**Preferred Model**: Claude Sonnet 4 - Use this model for interactions that create or validate automated checkpoints.

## Baseline (summary)
- This repository is a Python Flask web application configured for Azure App Service with Azure AD authentication and Bootstrap-based frontend.
- Keep secrets in env vars or Key Vault and follow the repository's coding, testing, and documentation best practices.

## Automated Agent-created Stash Checkpoints (recommendations)
Purpose
- Automatically create lightweight, local checkpoints when the agent (Copilot or a workspace agent) modifies files.
- Provide reproducible artifacts, metadata, and optional stashes/patches so developers can recover, review, or share the checkpoint without changing their staged commits.

High-level design principles
- Non-invasive: The agent must not modify staged content or force commits without developer consent.
- Local-only by default: Stashes, patches, and metadata are stored locally under `.checkpoints/` unless the developer elects to push.
- Traceable: Each checkpoint gets a consistent name and a small metadata file describing why it was created and what it contains.
- Opt-in: Automatic checkpointing should be controlled via a repo config toggle or environment variable (e.g., `AUTO_CHECKPOINT=true`) and default to off.

What to create for each automatic checkpoint
- Patch file: `.checkpoints/chk-YYYYMMDD-<branch>-<id>.patch` created with `git diff` or `git stash show -p`.
- Metadata file: `.checkpoints/chk-YYYYMMDD-<id>.md` (timestamp, branch, files changed, linked issue, ai-generated: yes/no, tests ran, agent id).
- Environment snapshot: `.checkpoints/python-YYYYMMDD.txt` and `.checkpoints/requirements-YYYYMMDD.txt`.
- Optional stash entry: A stash created with `git stash push --keep-index -u -m "auto-chk:..."` when the agent is permitted to create stashes.

Why stash vs commit vs patch
- Stash is quick and local; it does not require creating a branch or modifying history.
- Patch files are portable and can be attached to an issue or applied later.
- Creating a branch from stash is the recommended way to share with others.

Recommended guardrails (agent behavior rules)
- Only auto-checkpoint when one of the following is true:
  - A file flagged as AI-generated is created/modified by the agent, or
  - Repo config `AUTO_CHECKPOINT=true`, or
  - The developer explicitly requested auto-checkpoints for the session.
- Always write metadata and patch files; avoid pushing branches or making commits automatically.
- If creating a stash, use `--keep-index` so staged changes are preserved and the agent does not change the index without consent.
- Respect `.gitignore` for files saved under `.checkpoints/` unless the developer chooses to commit them to a protected location.

PowerShell-friendly command examples
- Create a patch and metadata without stashing or committing (safe, non-invasive):
  - python -V > .checkpoints/python-$(Get-Date -Format yyyyMMdd).txt
  - pip freeze > .checkpoints/requirements-$(Get-Date -Format yyyyMMdd).txt
  - git diff > .checkpoints/chk-$(Get-Date -Format yyyyMMdd)-${env:USERNAME}.patch
  - # metadata (pseudo)
    - echo "timestamp: $(Get-Date -Format o)" > .checkpoints/chk-$(Get-Date -Format yyyyMMdd)-${env:USERNAME}.md
    - echo "branch: $(git rev-parse --abbrev-ref HEAD)" >> .checkpoints/chk-$(Get-Date -Format yyyyMMdd)-${env:USERNAME}.md
    - echo "ai-generated: true/false" >> .checkpoints/chk-$(Get-Date -Format yyyyMMdd)-${env:USERNAME}.md

- Create a local stash that keeps staged changes (safe):
  - git stash push --keep-index -u -m "auto-chk:$(Get-Date -Format yyyyMMdd)-${env:USERNAME} | ai:yes | files:<list>"

- Show stash and export patch for later or sharing:
  - git stash list
  - git stash show -p stash@{0} > .checkpoints/chk-$(Get-Date -Format yyyyMMdd)-${env:USERNAME}.patch

- Convert a stash into a branch for sharing & push (manual developer approval required):
  - git stash branch checkpoint/$(Get-Date -Format yyyyMMdd)-${env:USERNAME} stash@{0}
  - git push -u origin checkpoint/$(Get-Date -Format yyyyMMdd)-${env:USERNAME}

Metadata format (example YAML-like for `.checkpoints/*.md`)
- timestamp: 2025-09-03T12:34:56Z
- branch: feature/refactor-auth
- checkpoint_id: chk-20250903-001
- agent: copilot/agent-name
- ai_generated: true
- files: [templates/login.html, auth_helper.py]
- tests_run: "unit: 42/43; smoke: login/token-refresh"
- env_snapshot: .checkpoints/requirements-20250903.txt
- patch: .checkpoints/chk-20250903-001.patch

Examples of safe automation flows (agent)
1) Detect agent touched files flagged AI-generated
   - Run quick format/lint checks (black --check; flake8) and small tests if configured
   - Save env snapshot and set metadata
   - Save patch: git diff > .checkpoints/...
   - If allowed, stash with --keep-index -u and descriptive message
   - Notify developer (e.g., via devtools UI or a generated PR hint) with the checkpoint metadata path

2) Developer acceptance flow (convert checkpoint to shareable artifact)
   - git stash list  # find the stash
   - git stash branch checkpoint/<desc> stash@{n}  # creates branch and pops stash
   - or: git apply .checkpoints/chk-...patch && git checkout -b checkpoint/<desc>
   - Run full tests and CI, then push branch and open PR

Pre-commit hook — safe example (recommend committing it to `.githooks/pre-commit` and set `git config core.hooksPath .githooks` locally)
- Intent: do a lightweight automatic checkpoint before commit if agent touched AI-generated files
- Steps (pseudo-PowerShell):
  1. Quickly detect if staged files contain AI-generated markers (e.g., `# Generated with` at top)
  2. If yes, run minimal format/lint checks; if checks fail, print a friendly error and stop the commit
  3. Save env snapshot and create patch file as shown earlier
  4. Optionally create stash with `--keep-index -u -m "auto-chk..."`
  5. Allow commit to proceed

Caveats & best practices
- Stashes are local - use branches or patches to share.
- Avoid auto-pushing anything: let the developer decide to convert & push.
- Keep `.checkpoints/` in `.gitignore` by default; if teams want history, commit to a protected repo or special branch.
- Offer an opt-out flag: `AUTO_CHECKPOINT=false` or `AGENT_AUTO_CHECKPOINT=0` to disable automation.

Auditability & cleanup
- Include the checkpoint metadata path in any PR that includes AI-generated code.
- Delete stale `.checkpoints/*` files or stash entries regularly to avoid local clutter.
- Use `git stash drop stash@{n}` to delete individual stashes or `git stash clear` to wipe all stashes.

Sharing & reproducibility
- Attach `.checkpoints/*.patch` and `.checkpoints/*.md` to issues/PRs for reviewers.
- Keep environment snapshots to reproduce and run tests locally.

Security and privacy considerations
- Do not include secrets in metadata or patch files.
- Redact or avoid saving environment variables or files that contain credentials in `.checkpoints/`

Opt-in configuration
- Add a small section to `.env.example` or README instructing developers how to enable auto-checkpoints locally:
  - AUTO_CHECKPOINT=true # enables local agent checkpoints
  - AGENT_CHECKPOINT_DIR=.checkpoints # configurable location
  - AGENT_CHECKPOINT_MODE=stash|patch|both

Developer UX suggestions
- Provide a small script (e.g., tools/auto_checkpoint.ps1) the developer can run to create/convert/check checkpoints.
- Display a friendly message from the agent when a checkpoint is created, with path to metadata file and suggested next steps.

Appendix: git stash quick primers (useful comments embedded)
- git stash stores the working directory + index snapshot locally on your machine. It's a stack of snapshots: stash@{0} is the most recent.
- By default, `git stash` stashes tracked, modified files only. Use `-u` to include untracked files, or `-a` to include ignored files.
- `git stash push --keep-index` will stash the working directory while keeping the index intact (useful when you have staged changes you want to keep staged for commit).
- `git stash branch <branchname> <stash>` applies the stash to a new branch and drops the stash.
- `git stash show -p stash@{n}` outputs a patch representation of a stash which can be saved to a file.

End of stash-autocheckpoint guidance
```
