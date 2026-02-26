# agent-skills

Repository for publishing reusable agent skills.

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `nblm-doc-review` | Review documents against NotebookLM notebooks and generate alignment reports | Active |
| `vendor-ddq-research` | Search and download vendor due diligence evidence based on DDQ requirements, including SOC report collection | Active |

## Repository Layout

```text
agent-skills/
├── README.md
├── nblm-doc-review/
│   ├── SKILL.md
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
