# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Quarto book** documenting the [AutoDeskR](https://github.com/paulgovan/AutoDeskR) R package, which provides an R interface to the AutoDesk Forge Platform APIs. The book covers authentication, data management, model derivatives, design automation, and the AutoDesk Viewer.

## Build Commands

``` bash
# Render the full book (HTML + PDF)
quarto render

# Render to a specific format
quarto render --to html
quarto render --to pdf

# Preview with live reload
quarto preview
```

Open `Book.Rproj` in RStudio to use the integrated project environment.

### PDF / EPUB downloads (build locally, do not render in CI)

The sidebar download menu (`downloads: [pdf, epub]` in `_quarto.yml`) serves
`docs/R-for-the-Built-Environment.pdf` and `.epub`. These are **built locally
and committed** — CI renders **HTML only**.

Reason: building PDF/EPUB makes Quarto rasterize the `{mermaid}` diagrams and
`rgl`/htmlwidget output with a headless Chrome, which hangs on the GitHub runner
and times the workflow out. Do **not** change the CI render steps back to a bare
`quarto render` (all formats); keep them as `quarto render --to html`.

To refresh the downloadable files after content changes, run ALL formats together (running them separately clears `docs/` each time, deleting the other formats):

``` bash
quarto render   # renders HTML + PDF + EPUB, then runs fix-epub.py
```

then commit the updated `docs/`.

## Architecture

The book has two layers of content:

1.  **Quarto chapters** (`*.qmd`) — the active build source defined in `_quarto.yml`. Currently contains introductory/stub content (index, intro, summary, references).

2.  **Legacy GitBook content** (`*.md` files and subdirectories) — the more complete API documentation referenced by `SUMMARY.md`. These are not yet wired into the Quarto build.

### Content Structure

-   `authentication.md` — OAuth token setup
-   `quick_start.md` — Package installation and overview
-   `viewer.md` — AutoDesk Viewer integration (large file, \~343KB)
-   `common-issues.md` — Troubleshooting guide
-   `data_management/` — OSS bucket and file upload tutorial
-   `model_derivative/` — File translation and data extraction tutorials
-   `design_automation/` — DWG-to-PDF conversion tutorial

### Configuration Files

-   `_quarto.yml` — Primary build config (HTML theme: cosmo, PDF class: scrreprt)
-   `book.json` — Legacy GitBook config (not used by Quarto build)
-   `references.bib` — Bibliography database
-   `Book.Rproj` — RStudio project file

## Key Integration Note

The legacy `.md` chapters (data_management, model_derivative, design_automation, etc.) are **not listed** in `_quarto.yml`'s chapter list. To include them in the Quarto build, add them under the `chapters:` key in `_quarto.yml`.
