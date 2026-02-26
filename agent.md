# Agent Skill Process

Use this checklist whenever you add or update a skill in this repository.

## 1) Repository setup

- Repo name: `agent-skills`
- Keep each skill at repo root (example: `nblm-doc-review/`)
- Keep repo description: `Repository for publishing agent skills.`

## 2) Add a new skill

1. Create folder: `<skill-name>/`
2. Add required file: `<skill-name>/SKILL.md`
3. Add optional folders if needed:
   - `<skill-name>/scripts/`
   - `<skill-name>/references/`
   - `<skill-name>/assets/`
4. Update top-level `README.md` skill table.

## 3) Update an existing skill

1. Edit files in the skill folder.
2. Avoid runtime-specific wording (keep instructions generic).
3. Keep paths as examples like `/path/to/...` unless required.

## 4) Commit directly to main

```bash
git add -A
git commit -m "<short clear message>"
git push origin main
```

## 5) Quick quality check

- Search for unwanted wording:
```bash
rg -n -i "claude|codex|vendor-neutral"
```
- If Python scripts changed:
```bash
python3 -m py_compile <skill-folder>/scripts/*.py
```

## 6) Naming rules

- Repo: `agent-skills`
- Skill folders: lowercase with hyphens (example: `doc-review`)
- Keep names short and clear.
