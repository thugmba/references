#!/usr/bin/env python3
"""Update and validate the thugmba/references GitHub Pages course bibliography.

Usage:
  python3 scripts/update_references_pages.py --write   # normalize source notes and regenerate docs
  python3 scripts/update_references_pages.py --check   # validation only; exits nonzero on issues
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Dict, Iterable, List, Tuple

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
SOURCE_ROOT = Path("/opt/data/workspace/06_Courses")
SECTION_ORDER = [
    "Academic Papers",
    "Books and Textbooks",
    "Articles and Reports",
    "Datasets, Tools, and Cases",
    "Videos and Media",
]
REFERENCE_SECTIONS = {"Academic Papers", "Articles and Reports"}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def strip_yaml(lines: List[str]) -> List[str]:
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1 :]
    return lines


def markdown_autolink_urls(text: str) -> str:
    """Make visible bare URLs clickable via <https://...> autolinks."""
    url_re = re.compile(r"https?://[^\s<>)]*")

    def repl(match: re.Match[str]) -> str:
        url = match.group(0)
        start, end = match.span()
        prev = text[start - 1] if start > 0 else ""
        nxt = text[end] if end < len(text) else ""
        if prev in "<(" or nxt == ">":
            return url
        trailing = ""
        while url and url[-1] in ". ,;:".replace(" ", ""):
            trailing = url[-1] + trailing
            url = url[:-1]
        return f"<{url}>{trailing}"

    return url_re.sub(repl, text)


def decode_one_google_news(url: str) -> str:
    """Decode a Google News RSS URL using googlenewsdecoder via uvx if needed."""
    code = (
        "from googlenewsdecoder import gnewsdecoder; import sys; "
        "r=gnewsdecoder(sys.argv[1], interval=0.4); "
        "print(r.get('decoded_url') if r.get('status') else '')"
    )
    result = subprocess.run(
        ["uvx", "--from", "googlenewsdecoder", "python", "-c", code, url],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=90,
        check=False,
    )
    decoded = result.stdout.strip().splitlines()[-1].strip() if result.stdout.strip() else ""
    if result.returncode == 0 and decoded.startswith("http"):
        return decoded
    raise RuntimeError(f"Could not decode Google News URL: {url[:120]} :: {result.stderr[:300]}")


def replace_google_news_urls(text: str, cache: Dict[str, str]) -> Tuple[str, int]:
    urls = list(dict.fromkeys(re.findall(r"https://news\.google\.com/rss/articles/[^\s<>)]*", text)))
    changed = 0
    for url in urls:
        if url not in cache:
            for attempt in range(3):
                try:
                    cache[url] = decode_one_google_news(url)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(1 + attempt)
        text = text.replace(url, cache[url])
        changed += 1
    return text, changed


def normalize_reference_text(text: str, *, decode_news: bool, cache: Dict[str, str]) -> str:
    text = re.sub(r"^###\s+Highly Relevant Updates\b.*\n?", "", text, flags=re.I | re.M)
    if decode_news:
        text, _ = replace_google_news_urls(text, cache)

    lines = text.splitlines()
    new: List[str] = []
    section = None
    for line in lines:
        msec = re.match(r"^##\s+(.+?)\s*$", line)
        if msec:
            section = msec.group(1).strip()
        if section in REFERENCE_SECTIONS:
            for pat in [r"^(\s*-\s+)\*([^*]+)\*(\s+.*)$", r"^(\s*\d+\.\s+)\*([^*]+)\*(\s+.*)$"]:
                m = re.match(pat, line)
                if m and not line.lstrip().startswith("- Teaching use:"):
                    line = f"{m.group(1)}**{m.group(2)}**{m.group(3)}"
                    break
        new.append(line)
    text = "\n".join(new) + "\n"
    text = markdown_autolink_urls(text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text


def parse_refs(path: Path) -> List[dict]:
    lines = strip_yaml(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    refs: List[dict] = []
    section = None
    current = None
    for line in lines:
        msec = re.match(r"^##\s+(.+?)\s*$", line)
        if msec:
            section = msec.group(1).strip()
            current = None
            continue
        if re.match(r"^###\s+", line):
            # Public pages do not expose status/subgroup headings.
            current = None
            continue
        if section and section.lower().startswith("maintenance"):
            continue
        if re.match(r"^-\s+\S", line):
            item = line[2:].strip()
            if not item or item in {"course-reference", "teaching-resources", "references"}:
                continue
            if item.startswith(("Add new references", "Link related course materials", "Keep this file")):
                continue
            current = {"text": item, "notes": [], "section": section or "References"}
            refs.append(current)
        elif current and re.match(r"^\s+-\s+\S", line):
            current["notes"].append(re.sub(r"^\s+-\s+", "", line).strip())
    return refs


def generate_docs() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    for old in list(DOCS.glob("*.html")) + list(DOCS.glob("*.css")) + [DOCS / ".nojekyll"]:
        if old.exists():
            old.unlink()

    courses = []
    for path in sorted(SOURCE_ROOT.glob("*/references.md")):
        course = path.parent.name
        refs = parse_refs(path)
        counts: Dict[str, int] = {}
        for ref in refs:
            counts[ref["section"]] = counts.get(ref["section"], 0) + 1
        courses.append({"course": course, "slug": slugify(course), "refs": refs, "counts": counts})

    updated = dt.date.today().isoformat()
    total = sum(len(c["refs"]) for c in courses)

    index = [
        "# Course Reference Lists",
        "",
        f"_Updated: {updated}_  ",
        f"_Courses: {len(courses)}_  ",
        f"_Total references: {total}_",
        "",
        "## Courses",
        "",
        "| Course | Total | Academic papers | Articles / reports |",
        "|---|---:|---:|---:|",
    ]
    for c in courses:
        index.append(
            f"| [{c['course']}]({c['slug']}.md) | {len(c['refs'])} | "
            f"{c['counts'].get('Academic Papers', 0)} | {c['counts'].get('Articles and Reports', 0)} |"
        )
    (DOCS / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    for c in courses:
        lines = [
            f"# {c['course']} — Reference List",
            "",
            f"_Updated: {updated}_  ",
            f"_Total references: {len(c['refs'])}_",
            "",
            "## Summary",
            "",
            "| Category | Count |",
            "|---|---:|",
        ]
        for sec in SECTION_ORDER:
            if c["counts"].get(sec):
                lines.append(f"| {sec} | {c['counts'][sec]} |")
        if not c["refs"]:
            lines.append("| Substantive references | 0 |")
        lines.append("")

        for sec in SECTION_ORDER:
            items = [r for r in c["refs"] if r["section"] == sec]
            if not items:
                continue
            lines += [f"## {sec}", ""]
            for idx, ref in enumerate(items, 1):
                lines.append(f"{idx}. {ref['text']}")
                for note in ref["notes"]:
                    lines.append(f"   - {note}")
                lines.append("")
        lines += ["---", "", "[Back to course reference index](index.md)", ""]
        (DOCS / f"{c['slug']}.md").write_text("\n".join(lines), encoding="utf-8")


def verify_paths(paths: Iterable[Path]) -> dict:
    report = {
        "files_checked": 0,
        "bare_url_issues": 0,
        "news_google": 0,
        "status_updates": 0,
        "highly_relevant_any": 0,
        "italic_title_entries": 0,
        "bold_title_entries": 0,
    }
    for path in paths:
        if not path.exists():
            continue
        report["files_checked"] += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        section = None
        for line in text.splitlines():
            msec = re.match(r"^##\s+(.+?)\s*$", line)
            if msec:
                section = msec.group(1).strip()
            for m in re.finditer(r"https?://[^\s<>)]*", line):
                prev = line[m.start() - 1] if m.start() > 0 else ""
                nxt = line[m.end()] if m.end() < len(line) else ""
                if prev not in "<(" and nxt != ">":
                    report["bare_url_issues"] += 1
            if section in REFERENCE_SECTIONS:
                if re.match(r"^\s*(?:\d+\.|-)\s+\*[^*]+\*\s+", line):
                    report["italic_title_entries"] += 1
                if re.match(r"^\s*(?:\d+\.|-)\s+\*\*[^*]+\*\*\s+", line):
                    report["bold_title_entries"] += 1
        report["news_google"] += text.count("news.google.com/rss/articles")
        report["status_updates"] += len(re.findall(r"^###\s+Highly Relevant Updates\b", text, re.I | re.M))
        report["highly_relevant_any"] += text.count("Highly Relevant")
    return report


def run_check() -> int:
    docs_report = verify_paths(DOCS.glob("*.md"))
    source_report = verify_paths(SOURCE_ROOT.glob("*/references.md"))
    summary = {"docs": docs_report, "source": source_report}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    fail_keys = ["bare_url_issues", "news_google", "status_updates", "italic_title_entries"]
    failed = any(docs_report[k] or source_report[k] for k in fail_keys)
    # Public docs should not expose any Highly Relevant status/group labels.
    failed = failed or docs_report["highly_relevant_any"] > 0
    return 1 if failed else 0


def run_write() -> int:
    cache: Dict[str, str] = {}
    for path in sorted(SOURCE_ROOT.glob("*/references.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        new_text = normalize_reference_text(text, decode_news=True, cache=cache)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
    generate_docs()
    return run_check()


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="normalize source notes and regenerate docs")
    group.add_argument("--check", action="store_true", help="validate source notes and docs only")
    args = parser.parse_args()
    return run_write() if args.write else run_check()


if __name__ == "__main__":
    raise SystemExit(main())
