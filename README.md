# Technology Standards (central manifest repository)

Single source of truth for approved technologies, policies, and the GitHub Copilot skill that
applies them. Every application repository is checked against this repo: by developers (Copilot skill),
on every pull request (GitHub Action), and across the whole portfolio (audit).

## How the pieces map to the pipeline diagram

| Diagram box | File(s) here |
|---|---|
| Standard Approved Technology / Dependency **YAML Manifest** | `manifest/technology-manifest.yaml` |
| Technology Standards Check **Copilot Skill (MD)** | `skills/standards-check/SKILL.md` (+ `scripts/check_standards.py`) |
| Compliance Report (frameworks, dependencies, version status) | Output of the skill / `check_standards.py` |
| **PR Pipeline Enforcement** (GitHub Action, Caution/Warn/Fail, Pass or Block) | `.github/workflows/standards-check.yml` (reusable) |
| **Monitoring**: Compliance Scan of all repos → Compliance Status Report → structured data → Power BI | `.github/workflows/portfolio-audit.yml` → `tools/audit.py` → `reports/compliance-status.csv` |
| **Technologies**: Technology Audit → query by framework → usage report | `tools/audit.py --tech <name>` → `reports/technology-usage-<name>.csv` |
| Policies the rules point to | `policies/*.md` (SEC, GOV, DOC, A11Y) |
| CMDB record each app keeps | `schemas/app-record.schema.md` (file `app-record.yaml` in each app repo) |

## Why YAML **and** Markdown
- **YAML = data.** The manifest, rules, exceptions and each app's `app-record.yaml` are structured data that
  scripts, Actions and AI can read and update precisely. This is the part that gets "uploaded" and versioned.
- **Markdown = instructions and documentation.** A Copilot skill is a `SKILL.md` file (Markdown with a small
  YAML header) that tells the AI *how* to use the YAML. Policies and generated docs are Markdown so people can read them.
- **Python = deterministic enforcement.** The same engine runs for the developer, the PR gate and the audit,
  so the AI and the pipeline can never disagree about what PASS means.

## Common tasks
```bash
pip install pyyaml
# Is a version approved?
python skills/standards-check/scripts/check_standards.py --manifest manifest/technology-manifest.yaml --lookup jquery 3.4.1
# Check a local app folder
python skills/standards-check/scripts/check_standards.py --manifest manifest/technology-manifest.yaml --repo ../road-info-blog
# Portfolio audit (needs gh auth login)
python tools/audit.py --owner gmale747
python tools/audit.py --owner gmale747 --tech bootstrap
```

## Changing the standards
Open a pull request. CODEOWNERS approval is required (GOV-05). `validate-manifest.yml` confirms the manifest still parses.
Tag a release (for example `v1.0.0`) after merging so `gh skill install` picks up the new skill version.
