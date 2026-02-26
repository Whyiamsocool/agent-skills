# agent-skills

Repository for publishing reusable agent skills.

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `nblm-doc-review` | Review documents against NotebookLM notebooks and generate alignment reports | Active |

## Repository Layout

```text
agent-skills/
├── README.md
├── nblm-doc-review/
│   ├── SKILL.md
│   ├── nblm-doc-review.skill
│   ├── scripts/
│   └── references/
└── <future-skill>/
```

## Adding a New Skill

1. Create `<skill-name>/`
2. Add `SKILL.md` with trigger conditions, workflow, and output format
3. Add optional `scripts/`, `references/`, and `assets/`
4. Update the table in this README

## Git Workflow

Direct commits to `main` are fine for this repository.
