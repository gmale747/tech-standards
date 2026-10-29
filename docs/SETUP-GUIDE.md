# Setup Guide: Technology Standards Pipeline with GitHub Copilot

Builds the whole pipeline from the diagram on your GitHub account (`gmale747`) using two repos:

| Repo | Role in the diagram |
|---|---|
| `tech-standards` | Central Manifest Repository: YAML manifest, policies, Copilot skill, reusable PR workflow, audit |
| `road-info-blog` | A "developer project": the test app being governed |

Each step ends with **✅ Confirm**. Don't move on until that's true.

---

## First, the big picture (YAML vs. Markdown)

Clint is right that **YAML is what you upload and maintain**, and the original Markdown idea still has a place:

| Layer | Format | What it is here |
|---|---|---|
| **Data / source of truth** | YAML | `manifest/technology-manifest.yaml` (approved versions, rules, exceptions) and each app's `app-record.yaml` (the CMDB record) |
| **AI instructions** | Markdown (+ small YAML header) | `SKILL.md`. GitHub Copilot skills *must* be Markdown. The skill tells Copilot how to use the YAML. |
| **Human docs** | Markdown | Policies and generated app docs |
| **Enforcement** | Python + GitHub Actions | One deterministic engine (`check_standards.py`) used by the skill, the PR gate, and the audits, so the AI and the pipeline always agree |

**Agentic vs. deterministic:** Copilot handles the judgment calls (explaining findings, fixing code, writing docs, safe metadata edits). The script handles the yes/no answers (is this version allowed?). Clint called this split out in your conversation, and this setup follows it.

---

## Part A: Prepare your machine

### Step 1: Install the tools
1. **Git**: https://git-scm.com/downloads
2. **GitHub CLI 2.90 or newer** (`gh skill` needs 2.90+): https://cli.github.com, then run `gh --version`
3. **Python 3.9+**, then run `pip install pyyaml`
4. **VS Code** with the **GitHub Copilot** and **GitHub Copilot Chat** extensions
5. Sign in: run `gh auth login` (choose GitHub.com, HTTPS, browser). In VS Code, click the Accounts icon and sign in to GitHub.

**✅ Confirm:** `gh auth status` shows `Logged in to github.com account gmale747`, and the Copilot icon in VS Code's status bar is not crossed out.

### Step 2: Check your Copilot plan and settings
1. Go to https://github.com/settings/copilot and confirm Copilot is active. Agent mode and skills in VS Code work on the individual plans. The Copilot cloud agent and Copilot code review depend on your plan.
2. In VS Code, open Settings (`Ctrl+,`) and search **skills**. If you see a setting such as `chat.useAgentSkills`, turn it on. Newer versions have skills on by default.

**✅ Confirm:** In Copilot Chat, the mode picker at the bottom of the chat box includes **Agent**.

---

## Part B: Publish the central standards repo

### Step 3: Create `tech-standards`
Unzip `tech-standards.zip`, then run:
```bash
cd tech-standards
git init -b main
git add .
git commit -m "Initial technology standards manifest, policies, skill, workflows"
gh repo create gmale747/tech-standards --public --source . --push
```
> **Public** keeps the test simple: app repos can call the reusable workflow, and the skill can download the manifest without a token. In production this would be an internal repo in an organization, with Actions access shared under *Settings → Actions → General → Access*.

**✅ Confirm:** https://github.com/gmale747/tech-standards shows `manifest/`, `policies/`, `skills/`, and `.github/workflows/`.

### Step 4: Tag a release
`gh skill install` installs from the latest release.
```bash
gh release create v1.0.0 --title "Standards v1.0.0" --notes "Initial manifest and skill"
```
**✅ Confirm:** The repo's **Actions** tab shows **Validate manifest** finished green.

### Step 5: Check the raw manifest URL
Open https://raw.githubusercontent.com/gmale747/tech-standards/main/manifest/technology-manifest.yaml in a browser.

**✅ Confirm:** You see the YAML text. The skill and its script read from this exact URL.

---

## Part C: Publish the test app

### Step 6: Create `road-info-blog`
Unzip `road-info-blog.zip`, then run:
```bash
cd road-info-blog
git init -b main
git add .
git commit -m "Initial road construction help blog"
gh repo create gmale747/road-info-blog --public --source . --push
```
The app already includes the four governance pieces:
- `app-record.yaml`: its CMDB record
- `.github/skills/standards-check/`: the Copilot skill, copied from the central repo
- `.github/copilot-instructions.md`: always-on guidance pointing Copilot to the skill
- `.github/workflows/standards-check.yml`: a three-line PR gate that calls the central workflow

**✅ Confirm:** The repo is on GitHub, and its **Actions** tab lists **Standards check**.

### Step 7: Run the site locally
```bash
python -m http.server 8080
```
Open http://localhost:8080. (Opening `index.html` by double-clicking won't work, because browsers block the CSV fetch from `file://`.)

**✅ Confirm:** The home page shows 10 articles, 8 categories, category bars, and cards. Clicking a card opens the article.

### Step 8 (optional): Publish with GitHub Pages
Go to repo **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**.

**✅ Confirm:** https://gmale747.github.io/road-info-blog/ loads within a couple of minutes. This is the `prod` URL in `app-record.yaml`.

---

## Part D: Use the skill as a developer (the "Developer Workflow" box)

### Step 9: Open the app in VS Code
```bash
code road-info-blog
```
Open Copilot Chat (`Ctrl+Alt+I`) and switch the mode to **Agent**.

**✅ Confirm:** Ask *"What skills are available in this workspace?"*. Copilot lists **standards-check**. If it doesn't, check Step 2 and reload the window.

### Step 10: Run a compliance check
Prompt:
> Run the Standards check on this repo and give me the compliance report.

Copilot loads the skill and asks permission to run `python .github/skills/standards-check/scripts/check_standards.py --repo .`. Click **Allow**.

**✅ Confirm:** You get a Compliance Report with **Overall: PASS**, a dependency table (bootstrap 5.3.3, papaparse 5.4.1 approved), and no policy findings.

### Step 11: Check a version before using it
Prompts to try:
> Is jQuery 3.4.1 approved? What should I use instead?

> I want to add Bootstrap 4.6.2. Is that allowed?

> Can I add left-pad?

**✅ Confirm:** jQuery 3.4.1 comes back **prohibited**, with a recommendation for 3.7.x. Bootstrap 4 is **deprecated** and shows its sunset date. left-pad is **not in the manifest** and needs architecture review (TECH-00).

### Step 12: Generate documentation
Prompt:
> Generate the application documentation for this app using the skill's template. Make an internal version.

**✅ Confirm:** A new `docs/app-overview.md` starts with the `<!-- generated -->` marker. Its facts match `app-record.yaml`, and it says `TODO:` where data is missing instead of inventing it.

Then ask for *"a public version"* and confirm that the owner and contact fields are left out.

### Step 13: Update app metadata safely (the AI-updates-YAML flow)
Prompts:
> Update the app version to 1.1.0.

> Change the owner to John Smith.

**✅ Confirm:** For the version, Copilot shows a before/after diff, waits for your OK, also updates `last_updated`, and re-runs the check. For the owner, it **refuses**, because `ownership.owner` is not in `auto_update_fields` (GOV-07).

### Step 14: Ask a policy question
> What does SEC-04 require, and does this repo meet it?

**✅ Confirm:** The answer cites SEC-04 (SRI on CDN resources) and points to the `integrity` attributes in `index.html`.

---

## Part E: PR enforcement (the "PR Pipeline Enforcement" box)

### Step 15: Open a non-compliant pull request
```bash
git checkout -b test/bad-deps
```
Make these edits:
- In `package.json`, change `"bootstrap": "5.3.3"` to `"bootstrap": "4.6.2"` and add `"jquery": "3.4.1"`.
- In `post.html`, change `<html lang="en">` to `<html>`.

Then push and open the pull request:
```bash
git commit -am "Test: introduce standards violations"
git push -u origin test/bad-deps
gh pr create --fill
```
**✅ Confirm:** On the PR, the **Standards check** fails ❌. A bot comment posts the Compliance Report (jQuery prohibited ❌, Bootstrap 4 deprecated 🟠, A11Y-01 ❌), and the **Files changed** tab shows inline annotations.

### Step 16: Make the check block merges
Go to repo **Settings → Rules → Rulesets → New ruleset → New branch ruleset**:
- Name: `standards-gate`. Enforcement: **Active**.
- Target branches: **Include default branch**.
- Turn on **Require a pull request before merging**.
- Turn on **Require status checks to pass**, click **Add checks**, and pick the check from Step 15 (it appears as `standards / Standards check`).
- Click **Create**.

**✅ Confirm:** The PR's **Merge** button is now blocked.

### Step 17: Fix the PR and watch it pass
Ask Copilot (Agent mode, on the `test/bad-deps` branch):
> Fix all the FAIL findings from the standards check.

Commit and push its changes.

**✅ Confirm:** The check turns green, the PR comment updates to PASS, and Merge becomes available. Close the PR or merge it.

### Step 18: See how an exception works
In the central repo's manifest, under `exceptions:`, there's an entry for app `legacy-permit-portal` / jQuery 3.4.1. If an app with that `app.id` uses jQuery 3.4.1, the result drops from FAIL to WARN until the exception expires. This is the "official exception" path from your conversation with Clint (GOV-04).

**✅ Confirm:** You can find the exception block and explain why it has an `expires` date.

---

## Part F: Monitoring and technology audits (the other two diagram lanes)

### Step 19: Run a full portfolio audit
Go to `tech-standards` → **Actions → Portfolio audit → Run workflow** and leave **tech** blank.

**✅ Confirm:** The run summary shows every repo under `gmale747` with an Overall status. Repos without `app-record.yaml` show **Onboarded: no** (that's your CMDB gap list). A new commit adds `reports/compliance-status.csv`, `reports/technology-usage.csv`, and `reports/summary.md`.

> The default token only sees **public** repos. For private ones, create a fine-grained token with **Contents: Read** on all repos and save it as the repo secret `AUDIT_TOKEN` (**Settings → Secrets and variables → Actions**).

### Step 20: Run a technology audit
Run **Portfolio audit** again with **tech** = `bootstrap`. You can also run it locally:
```bash
python tools/audit.py --owner gmale747 --tech bootstrap
```
**✅ Confirm:** `reports/technology-usage-bootstrap.csv` lists every repo, version, and status for Bootstrap. This is the "which apps use the vulnerable Log4j?" question, answered in one command.

### Step 21 (optional): Build a Power BI dashboard
In Power BI Desktop, go to **Get Data → Web** and use:
`https://raw.githubusercontent.com/gmale747/tech-standards/main/reports/compliance-status.csv`
Do the same for `technology-usage.csv`, and join the two on `repo`.

**✅ Confirm:** You can chart repos by Overall status and by department.

---

## Part G: Prove "change once, enforce everywhere"

### Step 22: Change a standard
In `tech-standards`, create a branch and edit the manifest. Change the papaparse rule so `">=5.4.0"` becomes `">=5.5.0"`, and `"<5.4.0"` becomes `"<5.5.0"` with `status: deprecated` and `sunset: 2027-01-31`. Open a PR, merge it, then re-run **Portfolio audit**.

**✅ Confirm:** Without touching `road-info-blog`, the audit now shows papaparse 5.4.1 as 🟠 deprecated, and so does the app's next PR check and its next Copilot check.

### Step 23: Onboard another app
In any other repo of yours:
1. Copy `app-record.yaml` from `road-info-blog` and edit it for that app.
2. Copy `.github/workflows/standards-check.yml` and `.github/copilot-instructions.md`.
3. Install the skill:
   ```bash
   gh skill install gmale747/tech-standards standards-check --agent github-copilot
   ```
   This installs into `.agents/skills/`, which Copilot reads. Alternatively, copy the folder into `.github/skills/`. Use `gh skill update` later to pull new skill versions.
4. Commit and push.

**✅ Confirm:** The next portfolio audit shows that repo as **Onboarded: yes**.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Copilot doesn't use the skill | Use Agent mode, mention "technology standards" in the prompt, reload the window, and check Step 2 |
| Copilot reports `PyYAML is required` | `pip install pyyaml` |
| PR comment step fails | Expected on PRs from forks (read-only token). The check itself still runs. |
| Reusable workflow "not found" | `tech-standards` must be public, or shared through Actions access settings |
| Blog shows "Could not load data/posts.csv" | Serve the folder over HTTP (Step 7) |

## Where Copilot reads things from
| Copilot feature | File | Used for |
|---|---|---|
| Repository custom instructions | `.github/copilot-instructions.md` | Always-on rules in every chat |
| Agent skill | `.github/skills/<name>/SKILL.md` or `.agents/skills/<name>/SKILL.md` | Loaded when relevant: checks, docs, metadata updates |
| Personal skill | `~/.copilot/skills/<name>/SKILL.md` | Your own skills across all repos |

Skills are supported in VS Code agent mode, Copilot CLI, the Copilot cloud agent, and Copilot code review.
