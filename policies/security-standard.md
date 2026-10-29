# Security Standard (SEC)

| | |
|---|---|
| Version | 1.0 |
| Owner | Information Security |
| Applies to | All Standards Lab application repositories |
| Enforcement | Automated (PR gate) where marked; otherwise code review |

## Rules

| ID | Rule | Enforcement | Severity |
|---|---|---|---|
| SEC-01 | No secrets (passwords, API keys, tokens, private keys) in source code or config. Use the approved secret store. | Automated | FAIL |
| SEC-02 | Use only technology versions approved in the technology manifest. Prohibited versions may not be merged. | Automated | Per manifest |
| SEC-03 | Load third-party scripts and stylesheets only from approved CDNs listed in the manifest. | Automated | FAIL |
| SEC-04 | Every CDN script and stylesheet has `integrity` (SRI) and `crossorigin` attributes. | Automated | FAIL |
| SEC-05 | External resources use HTTPS only. | Automated | FAIL |
| SEC-06 | Do not write untrusted data with `innerHTML`, `document.write`, or `eval`. Use `textContent` or a sanitizer. | Automated | WARN |
| SEC-07 | Every HTML page sets a Content-Security-Policy. | Automated | WARN |
| SEC-08 | Every repository has a `SECURITY.md` explaining how to report a vulnerability. | Automated (DOC-03) | FAIL |
| SEC-09 | No repository data, logs, or user data may be sent to an external AI service or connector without an approved data-flow review (see GOV-08). | Review | - |

## If a secret is committed
1. Rotate the secret immediately.
2. Remove it from git history.
3. Notify Information Security.
