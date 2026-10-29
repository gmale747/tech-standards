# App record schema (`app-record.yaml`)

Every application repository has this file at its root (GOV-01). Together, all app records form the CMDB.

```yaml
schema_version: 1
app:
  id: road-info-blog                 # required, unique, lowercase-hyphenated
  name: Road Construction Help Center # required
  description: >                     # required
    One or two sentences.
  ownership:
    department: Transportation Systems   # required; must be in manifest app_record.departments
    team: Public Information Web
    owner: Jane Doe                      # required
    escalation_contact: jane.doe@example.gov  # required
  access:
    visibility: public               # required: public | internal | restricted
    data_classification: public      # required: public | not-public | private | confidential
    roles_allowed: [developer, content-editor]
  metadata:
    version: 1.0.0                   # required, semantic version
    lifecycle: development           # required: development | production | retiring | retired
    last_updated: 2026-10-22
    tags: [web, static]
  repositories:
    primary_repo: https://github.com/<owner>/<repo>   # required
  environments:                      # any number of named environments
    prod:
      url: https://example.gov
      hosting: github-pages
      ip: 10.0.0.1                   # restricted audiences only
  documentation:
    readme: README.md
    runbook: docs/runbook.md
    security: SECURITY.md
  automation:                        # GOV-07
    allow_auto_updates: true
    auto_update_fields: [metadata.version, metadata.last_updated, metadata.tags]
```

Required fields and allowed values are enforced from `manifest/technology-manifest.yaml` (`app_record:` section).
