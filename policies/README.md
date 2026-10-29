# Policies

| Prefix | Policy | File |
|---|---|---|
| SEC | Security Standard | [security-standard.md](security-standard.md) |
| GOV | Governance Policy | [governance-policy.md](governance-policy.md) |
| DOC | Documentation Standard | [documentation-standard.md](documentation-standard.md) |
| A11Y | Accessibility Standard | [accessibility-standard.md](accessibility-standard.md) |
| TECH | Technology approval (see manifest) | [../manifest/technology-manifest.yaml](../manifest/technology-manifest.yaml) |

Rules marked "Automated" are implemented in `manifest/technology-manifest.yaml` (`rules:` section)
and enforced by `skills/standards-check/scripts/check_standards.py`.
