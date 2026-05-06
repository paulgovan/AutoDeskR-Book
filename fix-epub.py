#!/usr/bin/env python3
"""Post-render script: patch bare <figure class> in EPUB XHTML."""
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
            text = re.sub(r"<figure class>", '<figure class="figure">', text)
            data = text.encode("utf-8")
        zout.writestr(item, data)

os.replace(tmp, EPUB)
print(f'Patched {EPUB}: bare <figure class> -> <figure class="figure">')
