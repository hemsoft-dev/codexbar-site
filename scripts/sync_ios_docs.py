#!/usr/bin/env python3
"""Copy PRIVACY.md and SUPPORT.md from a codexbar-ios checkout into the site.

Usage: python3 scripts/sync_ios_docs.py /path/to/codexbar-ios

Rewrites the content between the BEGIN/END SYNC markers in privacy/index.html
and support/index.html. Standard library only; this is a maintenance tool, not
a build step. The site is deployed as committed HTML.
"""
import html
import pathlib
import re
import subprocess
import sys

SITE = pathlib.Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/hemsoft-dev/codexbar-ios"
TARGETS = {"PRIVACY.md": SITE / "privacy" / "index.html", "SUPPORT.md": SITE / "support" / "index.html"}
# Relative links in the Markdown that must point to pages on this site instead.
LINK_MAP = {"SUPPORT.md": "../support/", "PRIVACY.md": "../privacy/"}
LINK = re.compile(r"\[([^\]]+)\]\(((?:[^()\s]|\([^()]*\))+)\)")
INDENT = "        "


def inline(text):
    codes = []

    def keep(match):
        codes.append("<code>" + html.escape(match.group(1), quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    def restore(value):
        return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], value)

    def bold(escaped):
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)

    def link(match):
        # Escape the destination exactly once, from the raw Markdown, so query strings keep a single `&amp;`.
        href = html.escape(LINK_MAP.get(match.group(2), match.group(2)))
        label = restore(bold(html.escape(match.group(1), quote=False)))
        codes.append(f'<a href="{href}">{label}</a>')
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = LINK.sub(link, text)
    text = bold(html.escape(text, quote=False))
    return restore(text)


def convert(markdown):
    """Convert the Markdown subset used by these files: headings, paragraphs, lists, code, bold, links."""
    out, para, items = [], [], None

    def flush():
        nonlocal para, items
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if items is not None:
            out.append("<ul>")
            out.extend("  <li>" + inline(" ".join(item)) + "</li>" for item in items)
            out.append("</ul>")
            items = None

    for raw in markdown.splitlines():
        line = raw.rstrip()
        heading = re.match(r"^(#+)\s+(.*)$", line)
        if heading:
            flush()
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1:
                continue  # The page template supplies the h1.
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{slug}">{inline(text)}</h{level}>')
        elif not line.strip():
            flush()
        elif line.startswith("- "):
            if para:
                flush()
            if items is None:
                items = []
            items.append([line[2:].strip()])
        elif items is not None and raw.startswith("  "):
            items[-1].append(line.strip())
        else:
            if items is not None:
                flush()
            para.append(line.strip())
    flush()
    return out


def git(ios, *args):
    return subprocess.run(["git", "-C", str(ios), *args], check=True, capture_output=True, text=True).stdout.strip()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ios = pathlib.Path(sys.argv[1]).resolve()
    for name, target in TARGETS.items():
        sha, date = git(ios, "log", "-1", "--format=%H %cs", "--", name).split()
        # Read the committed text, never the working tree, so the page always matches the cited commit.
        source = git(ios, "show", f"{sha}:{name}") + "\n"
        note = [
            '<div class="source-note">',
            f'  <p>This page reproduces <a href="{REPO_URL}/blob/{sha}/{name}">{name}</a> from the codexbar-ios repository'
            f" (commit <code>{sha[:7]}</code>). Last updated: {date}.</p>",
        ]
        mapped = [key for key in LINK_MAP if f"]({key})" in source]
        if mapped:
            note.append("  <p>Links to " + " and ".join(mapped) + " point to the matching page on this site.</p>")
        note.append("</div>")
        body = note + convert(source)
        block = "\n".join(INDENT + line for line in body)
        page = target.read_text()
        pattern = re.compile(rf"(<!-- BEGIN SYNC {re.escape(name)} -->\n).*?(\s*<!-- END SYNC {re.escape(name)} -->)", re.S)
        if not pattern.search(page):
            sys.exit(f"Sync markers for {name} not found in {target}")
        target.write_text(pattern.sub(lambda m: m.group(1) + block + m.group(2), page))
        print(f"{name} @ {sha[:7]} ({date}) -> {target.relative_to(SITE)}")


if __name__ == "__main__":
    main()
