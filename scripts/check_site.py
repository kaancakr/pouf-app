#!/usr/bin/env python3
"""Checks the static site before it is published.

- Every relative href/src resolves to a file, and every #fragment to an id in its target
  (including symbols in the SVG icon sprite).
- Every English page has a Turkish twin under tr/ and the reverse.
- Every page has lang, a <title>, a canonical link and the en/tr hreflang pair.

Run from anywhere: python3 scripts/check_site.py. Exits 1 and lists the problems if any check fails.
"""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SKIPPED_SCHEMES = ("http", "https", "mailto")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.lang: str | None = None
        self.has_title = False
        self.has_canonical = False
        self.hreflangs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "html":
            self.lang = values.get("lang")
        if tag == "title":
            self.has_title = True
        if tag == "link":
            rel = values.get("rel", "")
            if rel == "canonical":
                self.has_canonical = True
            if rel == "alternate" and values.get("hreflang"):
                self.hreflangs.add(values["hreflang"])
            # canonical and alternate links are absolute URLs to the published site, not files to resolve
            if rel in ("canonical", "alternate"):
                return
        for name in ("href", "src"):
            if values.get(name):
                self.refs.append(values[name])


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def ids_in(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        cache[path] = parse(path).ids
    return cache[path]


def check_refs(page: Path, parser: PageParser, id_cache: dict[Path, set[str]]) -> list[str]:
    problems = []
    for ref in parser.refs:
        parts = urlsplit(ref)
        if parts.scheme in SKIPPED_SCHEMES:
            continue
        if parts.scheme:
            problems.append(f"{page.relative_to(ROOT)}: unexpected scheme in {ref!r}")
            continue
        target = page if not parts.path else (page.parent / parts.path).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            problems.append(f"{page.relative_to(ROOT)}: {ref!r} points to a missing file")
            continue
        if not str(target).startswith(str(ROOT)):
            problems.append(f"{page.relative_to(ROOT)}: {ref!r} leaves the site folder")
            continue
        if parts.fragment and target.suffix in (".html", ".svg"):
            if parts.fragment not in ids_in(target, id_cache):
                problems.append(f"{page.relative_to(ROOT)}: {ref!r} has no id {parts.fragment!r} in its target")
    return problems


def check_page_meta(page: Path, parser: PageParser) -> list[str]:
    name = page.relative_to(ROOT)
    expected_lang = "tr" if name.parts[0] == "tr" else "en"
    problems = []
    if parser.lang != expected_lang:
        problems.append(f"{name}: lang is {parser.lang!r}, expected {expected_lang!r}")
    if not parser.has_title:
        problems.append(f"{name}: no <title>")
    if not parser.has_canonical:
        problems.append(f"{name}: no canonical link")
    if parser.hreflangs != {"en", "tr", "x-default"}:
        problems.append(f"{name}: hreflang links are {sorted(parser.hreflangs)}, expected en, tr and x-default")
    return problems


def check_twins(pages: list[Path]) -> list[str]:
    relative = {page.relative_to(ROOT) for page in pages}
    english = {path for path in relative if path.parts[0] != "tr"}
    turkish = {Path(*path.parts[1:]) for path in relative if path.parts[0] == "tr"}
    problems = [f"{path}: no Turkish twin at tr/{path}" for path in sorted(english - turkish)]
    problems += [f"tr/{path}: no English twin at {path}" for path in sorted(turkish - english)]
    return problems


def main() -> int:
    pages = sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)
    if not pages:
        print("check_site: no HTML pages found", file=sys.stderr)
        return 1
    id_cache: dict[Path, set[str]] = {}
    problems: list[str] = []
    for page in pages:
        parser = parse(page)
        problems += check_refs(page, parser, id_cache)
        problems += check_page_meta(page, parser)
    problems += check_twins(pages)
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"check_site: {len(pages)} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
