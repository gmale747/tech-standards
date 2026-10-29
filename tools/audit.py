#!/usr/bin/env python3
"""
Portfolio audit: runs the standards check across many repositories.

Produces the Monitoring and Technology Audit outputs from the pipeline diagram:
  reports/compliance-status.csv   one row per repo: CMDB fields + overall status   (Compliance Status Report / CMDB)
  reports/technology-usage.csv    one row per repo x technology x version          (Technology Usage Report)
  reports/summary.md              human-readable roll-up
These CSVs are the "structured" layer a Power BI / analytics dashboard can read directly.

Examples:
  python tools/audit.py --owner gmale747                       # full audit of every repo the token can see
  python tools/audit.py --owner gmale747 --tech jquery         # who uses jQuery, and which versions?
  python tools/audit.py --local ../road-info-blog ../other-app # audit local folders (no GitHub needed)

Requires: Python 3.9+, PyYAML, git, and the GitHub CLI (gh) for --owner mode.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "skills" / "standards-check" / "scripts"))
import check_standards as cs  # noqa: E402


def list_repos(owner: str, skip: list[str]) -> list[dict]:
    out = subprocess.run(
        ["gh", "repo", "list", owner, "--limit", "1000", "--no-archived", "--json", "name,url,isPrivate"],
        check=True, capture_output=True, text=True).stdout
    return [r for r in json.loads(out) if r["name"] not in skip]


def clone(owner: str, name: str, dest: Path) -> Path:
    target = dest / name
    subprocess.run(["gh", "repo", "clone", f"{owner}/{name}", str(target), "--", "--depth", "1", "--quiet"],
                   check=True, capture_output=True)
    return target


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--owner", help="GitHub user or organization to scan")
    src.add_argument("--local", nargs="+", help="local repository folders to scan")
    ap.add_argument("--manifest", default=str(ROOT / "manifest" / "technology-manifest.yaml"))
    ap.add_argument("--tech", help="technology audit: only report this technology (name or alias)")
    ap.add_argument("--out", default=str(ROOT / "reports"))
    ap.add_argument("--skip", nargs="*", default=["tech-standards"], help="repo names to skip")
    args = ap.parse_args(argv)

    manifest = cs.load_manifest(args.manifest)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="standards-audit-"))

    targets: list[tuple[str, Path | None, str]] = []
    if args.owner:
        for r in list_repos(args.owner, args.skip):
            try:
                targets.append((r["name"], clone(args.owner, r["name"], tmp), r["url"]))
            except subprocess.CalledProcessError:
                targets.append((r["name"], None, r["url"]))
    else:
        targets = [(Path(p).resolve().name, Path(p), str(Path(p).resolve())) for p in args.local]

    status_rows, tech_rows = [], []
    tech_filter = None
    if args.tech:
        t = cs.find_technology(manifest, args.tech)
        tech_filter = (t["name"] if t else args.tech).lower()

    for name, path, url in targets:
        if path is None:
            status_rows.append({"repo": name, "url": url, "onboarded": "clone-failed"})
            continue
        report = cs.run_check(path, manifest)
        onboarded = "yes" if (path / "app-record.yaml").exists() else "no"
        a = report["app"]
        status_rows.append({
            "repo": name, "url": url, "onboarded": onboarded,
            "app_id": a["id"], "app_name": a["name"], "department": a["department"], "owner": a["owner"],
            "visibility": a["visibility"], "data_classification": a["data_classification"],
            "app_version": a["version"], "lifecycle": a["lifecycle"],
            "overall": report["overall"], "fail": report["counts"]["FAIL"], "warn": report["counts"]["WARN"],
            "caution": report["counts"]["CAUTION"], "manifest_version": report["manifest_version"],
            "checked_at": report["checked_at"],
        })
        for d in report["dependencies"]:
            if tech_filter and d["technology"].lower() != tech_filter:
                continue
            tech_rows.append({
                "repo": name, "app_id": a["id"], "department": a["department"],
                "technology": d["technology"], "category": d["category"], "version": d["version"],
                "status": d["status"], "level": d["level"], "ecosystem": d["ecosystem"],
                "found_in": ";".join(d["sources"]), "note": d["note"],
            })

    shutil.rmtree(tmp, ignore_errors=True)
    suffix = f"-{tech_filter}" if tech_filter else ""
    write_csv(out / "compliance-status.csv", status_rows)
    write_csv(out / f"technology-usage{suffix}.csv", tech_rows)
    summary = build_summary(status_rows, tech_rows, tech_filter, manifest)
    (out / f"summary{suffix}.md").write_text(summary, encoding="utf-8")
    print(summary)


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def build_summary(status_rows, tech_rows, tech_filter, manifest) -> str:
    icon = cs.LEVEL_ICON
    L = [f"# Standards Lab {'Technology Audit: ' + tech_filter if tech_filter else 'Portfolio Compliance Audit'}", "",
         f"Manifest v{manifest.get('manifest_version')} · {len(status_rows)} repositories scanned", ""]
    if not tech_filter:
        by = {}
        for r in status_rows:
            by[r.get("overall", "NOT ONBOARDED")] = by.get(r.get("overall", "NOT ONBOARDED"), 0) + 1
        L += ["| Overall | Repos |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(by.items())] + [""]
        L += ["| Repo | Onboarded | Department | Owner | Overall | Fail | Warn |", "|---|---|---|---|---|---|---|"]
        for r in sorted(status_rows, key=lambda r: -cs.LEVEL_RANK.get(r.get("overall", "PASS"), 0)):
            ov = r.get("overall", "—")
            L.append(f"| {r['repo']} | {r['onboarded']} | {r.get('department') or '—'} | {r.get('owner') or '—'} | "
                     f"{icon.get(ov, '')} {ov} | {r.get('fail', '')} | {r.get('warn', '')} |")
        L.append("")
    L += ["## Technology usage", "", "| Technology | Version | Status | Repo | Department |", "|---|---|---|---|---|"]
    for t in sorted(tech_rows, key=lambda t: (t["technology"], t["version"], t["repo"])):
        L.append(f"| {t['technology']} | {t['version']} | {icon[t['level']]} {t['status']} | {t['repo']} | "
                 f"{t['department'] or '—'} |")
    if not tech_rows:
        L.append("| _none found_ | | | | |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
