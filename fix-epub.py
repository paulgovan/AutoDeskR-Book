#!/usr/bin/env python3
"""Post-render script: patch malformed figure XHTML in EPUB.

Quarto wraps mermaid diagram <figure> open/close tags each in their own
<p>...</p>, producing invalid XHTML:

    <p><figure class="figure"></p>   ← figure opens, then </p> mismatches
    <div><p><img .../></p></div>
    <p></figure></p>                 ← spurious <p> wrapper

This is invalid XML (EPUB validators and some readers reject it with
"Opening and ending tag mismatch: figure … and p"). Strip the spurious
<p> wrappers so the structure becomes:

    <figure class="figure">
    <div><p><img .../></p></div>
    </figure>

Also fix any leftover bare <figure class> attributes (older Quarto behavior).
"""
import os
import re
import zipfile

EPUB = "docs/R-for-the-Built-Environment.epub"

if not os.path.exists(EPUB):
    raise SystemExit(0)

tmp = EPUB + ".tmp"
with zipfile.ZipFile(EPUB, "r") as zin, \
     zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.endswith(".xhtml"):
            text = data.decode("utf-8")
            # Remove spurious <p>…</p> wrapper around <figure> opening tag
            text = re.sub(r'<p>(<figure\b[^>]*>)</p>', r'\1', text)
            # Remove spurious <p>…</p> wrapper around </figure> closing tag
            text = re.sub(r'<p>(</figure>)</p>', r'\1', text)
            # Fix any remaining bare class attributes (legacy Quarto output)
            text = re.sub(r"<figure class>", '<figure class="figure">', text)
            data = text.encode("utf-8")
        zout.writestr(item, data)

os.replace(tmp, EPUB)
print(f"Patched {EPUB}: fixed malformed <figure> XHTML wrappers")
