#!/usr/bin/env python3
"""Post-render script: patch the rendered EPUB for KDP/Kindle readiness.

Two fixes are applied to the EPUB's XHTML:

1. Malformed <figure> wrappers. Quarto wraps mermaid diagram <figure>
   open/close tags each in their own <p>...</p>, producing invalid XHTML
   ("Opening and ending tag mismatch: figure ... and p"). Strip the spurious
   <p> wrappers, and fix any bare <figure class> attributes.

2. Broken cross-reference links. Quarto resolves inter-chapter links like
   [Viewer](viewer.qmd) correctly for HTML (-> viewer.html) but leaves the
   raw `.qmd` href in the EPUB, producing broken internal links that
   epubcheck/KDP reject. Rewrite each `name.qmd` href to the chapter's
   bundled `chNNN.xhtml` file, mapped via the chapter title slug.
"""
import glob
import os
import re
import zipfile

epubs = glob.glob("docs/*.epub")
if not epubs:
    raise SystemExit(0)
EPUB = epubs[0]


def slugify(title):
    """Replicate Pandoc's auto-identifier algorithm for a heading/title."""
    t = title.strip().lower()
    t = re.sub(r"[^\w\s\-.]", "", t)   # keep alphanumerics, _, space, -, .
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"^[^a-z]+", "", t)      # identifiers may not begin with a digit/punct
    return t or "section"


# Map each project .qmd to its chapter title slug.
qmd_slug = {}
for f in glob.glob("*.qmd"):
    txt = open(f, encoding="utf-8").read()
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', txt, re.M)
    if m:
        title = m.group(1)
    else:
        m2 = re.search(r"^#\s+(.+?)\s*(?:\{.*\})?$", txt, re.M)
        title = m2.group(1) if m2 else None
    if title:
        qmd_slug[os.path.basename(f)] = slugify(title)

# Read the EPUB once into memory.
with zipfile.ZipFile(EPUB) as zin:
    entries = [(info, zin.read(info.filename)) for info in zin.infolist()]

# Build slug -> chapter file (chNNN.xhtml) from each chapter's first <section id>.
slug_to_file = {}
for info, data in entries:
    if re.search(r"text/ch\d+\.xhtml$", info.filename):
        m = re.search(rb'<section[^>]*\bid="([^"]+)"', data)
        if m:
            slug_to_file[m.group(1).decode()] = os.path.basename(info.filename)

# Resolve .qmd basename -> chapter file.
qmd_to_file = {q: slug_to_file[s] for q, s in qmd_slug.items() if s in slug_to_file}

link_re = re.compile(r'href="(?:\./)?([A-Za-z0-9_\-]+\.qmd)(#[^"]*)?"')
counters = {"links": 0, "unresolved": set()}


def fix_links(text):
    def repl(mo):
        qmd, anchor = mo.group(1), mo.group(2) or ""
        target = qmd_to_file.get(qmd)
        if target:
            counters["links"] += 1
            return f'href="{target}{anchor}"'
        counters["unresolved"].add(qmd)
        return mo.group(0)
    return link_re.sub(repl, text)


tmp = EPUB + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for info, data in entries:
        if info.filename.endswith(".xhtml"):
            text = data.decode("utf-8")
            # 1. Malformed <figure> XHTML
            text = re.sub(r"<p>(<figure\b[^>]*>)</p>", r"\1", text)
            text = re.sub(r"<p>(</figure>)</p>", r"\1", text)
            text = re.sub(r"<figure class>", '<figure class="figure">', text)
            # 2. Broken .qmd cross-reference links
            text = fix_links(text)
            data = text.encode("utf-8")
        # info carries the original compress_type, so `mimetype` stays stored.
        zout.writestr(info, data)

os.replace(tmp, EPUB)
msg = f"Patched {EPUB}: fixed <figure> XHTML, rewrote {counters['links']} .qmd cross-links"
if counters["unresolved"]:
    msg += f" (unresolved: {sorted(counters['unresolved'])})"
print(msg)
