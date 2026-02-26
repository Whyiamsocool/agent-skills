# agent-skills

A repository of reusable, vendor-neutral agent skills.

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `nblm-doc-review` | Review documents against NotebookLM notebooks and generate alignment reports | Active |

## Repository Layout

```text
agent-skills/
├── README.md
└── skills/
    └── nblm-doc-review/
        ├── SKILL.md
        ├── nblm-doc-review.skill
        ├── scripts/
        └── references/
```

## Adding a New Skill

1. Create `skills/<skill-name>/`
2. Add `SKILL.md` with trigger conditions, workflow, and output format
3. Add optional `scripts/`, `references/`, and `assets/`
4. Update the table in this README

## Recommended Git Workflow

1. Create branch `feature/<short-change-name>`
2. Commit your changes
3. Open a pull request to `main`
4. Merge after review/checks

For tiny typo fixes, direct commits are acceptable.
