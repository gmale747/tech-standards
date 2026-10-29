# Governance Policy (GOV)

| | |
|---|---|
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Applies to | All Standards Lab application repositories and the standards repository |

## Rules

| ID | Rule |
|---|---|
| GOV-01 | Every application repository has an app record, `app-record.yaml`, at its root. This is the application's CMDB entry. |
| GOV-02 | The app record is complete and uses allowed values (department, visibility, data classification, lifecycle). See `schemas/app-record.schema.md`. |
| GOV-03 | Changes reach the default branch only through a pull request that passes the Standards check. Branch protection or a ruleset requires the check. |
| GOV-04 | Exceptions to a FAIL are requested by ticket, approved by the Enterprise Architecture Review Board, recorded in the manifest `exceptions` section, and always have an expiry date. |
| GOV-05 | The manifest and policies change only through a pull request to the standards repository, approved by CODEOWNERS. |
| GOV-06 | Deprecated technology is removed before its sunset date. After the sunset date it is treated as prohibited. |
| GOV-07 | AI agents may update an app record only in fields listed in `automation.auto_update_fields`, must show a diff, and require human approval through a pull request. |
| GOV-08 | AI skills, connectors, or integrations that send state data outside the approved boundary require a data-flow review before use. |

## Severity and outcome
| Level | Meaning | PR outcome |
|---|---|---|
| PASS | Approved | Merge allowed |
| CAUTION | Allowed; upgrade should be planned | Merge allowed |
| WARN | Deprecated, unlisted, or a recommended practice is missing | Merge allowed; owner reviews |
| FAIL | Prohibited or a required control is missing | Merge blocked unless GOV-04 exception |

## Roles
- **Application owner**: keeps the app record current, fixes findings.
- **Enterprise Architecture**: owns the manifest; approves new technologies (TECH-00 reviews).
- **Review Board**: approves exceptions.
