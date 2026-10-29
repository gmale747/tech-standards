# Documentation Standard (DOC)

| | |
|---|---|
| Version | 1.0 |
| Owner | Enterprise Architecture |

Documentation is treated as code: it lives in the repository, in Markdown, and is reviewed in pull requests.

| ID | Rule |
|---|---|
| DOC-01 | `README.md` explains purpose, how to run locally, and how it is deployed. |
| DOC-02 | `docs/runbook.md` covers run, deploy, health check, rollback, and contacts. |
| DOC-03 | `SECURITY.md` explains vulnerability reporting and key security controls. |
| DOC-04 | Source documentation is Markdown. Word files are not used as the source; export to PDF or Word when needed. |
| DOC-05 | Generated documents (for example `docs/app-overview.md`) are produced from `app-record.yaml` and the template, carry a `generated` marker, and are not hand-edited. |

## Audience levels for generated documents
| Audience | May include |
|---|---|
| public | Name, description, public URL, technology stack |
| internal | Everything in public, plus owner, team, contacts, all environments |
| restricted | Everything, including IP addresses and hosting details |
