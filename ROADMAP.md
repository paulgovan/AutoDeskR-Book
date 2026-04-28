# R and the AutoDesk Platform — Roadmap

> Last updated: 2026-04-23\
> Covers: book content gaps, package coverage gaps, and quality improvements.\
> Based on an audit of the [AutoDeskR](https://github.com/paulgovan/AutoDeskR) source (v0.4.0) against the full [APS API catalogue](https://aps.autodesk.com/developer/documentation).

------------------------------------------------------------------------

## 1 · Immediate Priority — Document Already-Implemented APIs

These functions exist in the package but have **no book chapter**. Zero new code required — documentation only.

### 1.1 Reality Capture ⭐ highest priority

**Package functions (all implemented):**

| Function              | Description                       |
|-----------------------|-----------------------------------|
| `createPhotoscene()`  | Create a new photogrammetry scene |
| `uploadImages()`      | Upload photos to a photoscene     |
| `processPhotoscene()` | Kick off 3D reconstruction        |
| `checkPhotoscene()`   | Poll job status                   |
| `waitForPhotoscene()` | Block until processing completes  |

**Chapter outline for `reality-capture.qmd`:** 1. What is Reality Capture? (photogrammetry, drone/UAV inputs) 2. Prerequisites — image guidelines (overlap %, lighting, GPS tags) 3. End-to-end workflow with mock responses: - `createPhotoscene()` → photoscene ID - `uploadImages()` → upload confirmation - `processPhotoscene()` → job submission response - `checkPhotoscene()` / `waitForPhotoscene()` → progress polling 4. Downloading the output mesh 5. Callout: file-size and image-count limits on the free tier

**`_quarto.yml` change needed:** Add `reality-capture.qmd` under the `"API Reference"` part.

------------------------------------------------------------------------

## 2 · Near-Term — Book Quality Improvements

Improvements to existing chapters that require no package changes.

| \# | Item | Effort | Description |
|----|----|----|----|
| 2.1 | Fill `references.bib` | Low | Add citations for APS docs, httr2, jsonlite, Shiny, R itself; add `[@ref]` callouts in text |
| 2.2 | Warning callout blocks | Low | Add `:::callout-warning` for: token expiry (1 h), globally-unique bucket names, OBJ format restrictions, bucket-must-be-empty before deletion |
| 2.3 | Error-path mock responses | Low | Show what `401 Unauthorized` and `409 Conflict` look like in `resp$content`; link to `troubleshooting.qmd` |
| 2.4 | Rate-limit / retry guidance | Medium | Add polling loop pattern with `Sys.sleep()` and mention HTTP 429 in each chapter |
| 2.5 | Getting Started flowchart | Medium | Mermaid diagram: authenticate → bucket → upload → translate → view; add to `getting-started.qmd` |
| 2.6 | PDF/print polish | Medium | Add `geometry`, `fontsize`, `colorlinks` YAML to `_quarto.yml` for `scrreprt` output |
| 2.7 | End-to-end case study chapter | High | New `case-study.qmd`: "From DWG to Shiny Dashboard" — single narrative tying all six APIs together using `aerial.dwg` sample file |
| 2.8 | Function reference appendix | High | New `reference.qmd`: table of every exported function with required scopes and key parameters |

------------------------------------------------------------------------

## 3 · Medium-Term — Package + Book Gaps

APIs that exist in APS but are **not implemented** in AutoDeskR. Each would need new R functions *and* a new book chapter.

### 3.1 Hierarchical Data Management (ACC / BIM 360 project structure)

The current package only covers OSS (flat bucket storage). APS also exposes a richer project hierarchy:

```         
Hub → Project → Folder → Item → Version
```

**Functions to add:** - `listHubs()`, `getHub()` - `listProjects()`, `getProject()` - `listFolders()`, `listFolderContents()` - `listItems()`, `getItem()`, `getItemVersions()`

**Why it matters:** Required for working with BIM 360 and ACC projects, where files live in a managed folder tree rather than flat OSS buckets.

------------------------------------------------------------------------

### 3.2 Webhooks API

APS can push HTTP callbacks when files are translated, issues change, versions are created, etc.

**Functions to add:** - `createWebhook()` — register a callback URL for an event - `listWebhooks()` — list active subscriptions - `deleteWebhook()` — remove a subscription

**Why it matters:** Enables event-driven pipelines (e.g. auto-translate a file the moment it is uploaded) without polling.

------------------------------------------------------------------------

### 3.3 Construction Issues API

Project issue tracking exposed via REST.

**Functions to add:** - `listIssues()` — list all issues in a project - `getIssue()` — get a single issue - `createIssue()` — create a new issue - `updateIssue()` — update status / assignee - `listIssueTypes()` — available types and subtypes

**Why it matters:** Allows R-based dashboards to surface live project health data alongside model analytics.

------------------------------------------------------------------------

### 3.4 Account Admin API

Project, user, and company management.

**Functions to add:** - `listAccounts()`, `createProject()` - `listUsers()`, `addUser()`, `removeUser()` - `listCompanies()`

------------------------------------------------------------------------

### 3.5 Advanced Design Automation

The current `makePdf()` / `checkPdf()` only wraps the DWG→PDF workflow. APS Design Automation also supports:

| Engine   | Capability                                   |
|----------|----------------------------------------------|
| AutoCAD  | Run custom LISP/scripts on DWG files         |
| Revit    | Export sheets, schedules, run custom add-ins |
| 3ds Max  | Render scenes                                |
| Inventor | Generate drawings, BOMs                      |
| Fusion   | Export CAM toolpaths                         |

**Functions to add:** Generalised `submitWorkItem()`, `listEngines()`, `listActivities()` — engine-agnostic wrappers that accept a payload and engine name.

------------------------------------------------------------------------

## 4 · MCP Server (AI Agent Integration)

### 4.1 Overview

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open standard that lets AI assistants (Claude, Copilot, etc.) call external tools as part of a conversation. Exposing AutoDeskR as an MCP server would allow an AI agent to query BIM models, translate files, extract layer data, and generate reports — all without a human writing R code.

This is the highest-leverage emerging opportunity: it rides the AI agent wave without requiring changes to the core package API.

### 4.2 Proposed MCP Tools

Each tool wraps one or more existing AutoDeskR functions:

| MCP Tool | Wraps | Description |
|---|---|---|
| `get_token` | `getToken()` | Authenticate and return a bearer token |
| `upload_file` | `makeBucket()` + `uploadFile()` | Create a bucket and upload a local file |
| `translate_file` | `translateObj()` / `translateSvf()` + `checkFile()` | Translate a file and poll until complete |
| `get_layer_summary` | `translateSvf()` + `getData()` | Return a layer-level object count and area summary for a DWG |
| `get_object_tree` | `getObjectTree()` | Return the model hierarchy as a JSON tree |
| `get_metadata` | `getMetadata()` | List available metadata GUIDs for a translated model |
| `download_mesh` | `getOutputUrn()` + `downloadFile()` | Download the translated OBJ/STL to a local path |
| `make_pdf` | `makePdf()` + `checkPdf()` | Convert a DWG to PDF via Design Automation |
| `get_sensor_streams` | Tandem REST API | List sensor streams for a Tandem facility |
| `get_stream_readings` | Tandem REST API | Fetch time-series readings for a stream |

### 4.3 Implementation Approach

An MCP server for R can be built using the [`mcpr`](https://github.com/devOpifex/mcpr) package or by implementing the JSON-RPC 2.0 transport directly with `httpuv`. The server would:

1. Receive a tool call (JSON-RPC over stdio or HTTP/SSE)
2. Authenticate using credentials from environment variables
3. Call the relevant AutoDeskR function(s)
4. Return the result as a structured JSON response

```r
# Illustrative — not yet implemented
library(mcpr)

mcp_tool("get_layer_summary",
  description = "Return object count and area by layer for a DWG file URN",
  params = list(urn = "string", token = "string"),
  handler = function(urn, token) {
    encoded <- jsonlite::base64_enc(urn)
    resp    <- getData(urn = encoded, token = token)
    summarise_layers(resp$content)   # internal helper
  }
)
```

### 4.4 Book Chapter

Add `mcp-server.qmd` to the Reference part:

- What MCP is and why it matters for BIM workflows
- Setting up the AutoDeskR MCP server locally
- Connecting it to Claude Desktop or VS Code Copilot
- Example agent conversations: "Summarise the layers in this DWG", "Compare these two drawing revisions", "Show me the sensor readings for HVAC zone 3"
- Security considerations: credential scoping, rate limits, token expiry

### 4.5 Strategic Note

An MCP server transforms AutoDeskR from a package analysts use into infrastructure that AI agents use. The audience expands from R practitioners to anyone with an AI assistant and a pile of CAD files. This does not require changes to existing package functions — only a new thin server layer on top.

------------------------------------------------------------------------

## 5 · Long-Term / Exploratory

| API | Notes |
|----|----|
| **Model Coordination** | Clash detection, model sets — primarily ACC-specific; requires project hierarchy (§3.1) first |
| **Tandem (Digital Twins)** | Operational sensor data linked to BIM models; still maturing |
| **Forma** | AEC industry cloud; separate SDK emerging |
| **Fusion Data Model** | Manufacturing-focused; different audience from the current book |
| **Cost Management** | Budget webhooks and financial data; useful for project dashboards |

------------------------------------------------------------------------

## 6 · Suggested Chapter Order After Expansion

``` yaml
chapters:
  - index.qmd               # Preface
  - part: "Front Matter"
    chapters:
      - motivation.qmd
      - getting-started.qmd
      - acknowledgements.qmd
      - license.qmd
  - part: "Core APIs"
    chapters:
      - authentication.qmd
      - data-management.qmd
      - model-derivative.qmd
      - design-automation.qmd
      - reality-capture.qmd  # ← add next
      - viewer.qmd
  - part: "Project & Account APIs"    # ← future
    chapters:
      - data-management-acc.qmd
      - construction-issues.qmd
      - account-admin.qmd
      - webhooks.qmd
  - part: "Reference"
    chapters:
      - case-study.qmd       # ← near-term
      - reference.qmd        # ← near-term
      - troubleshooting.qmd
  - references.qmd
```

------------------------------------------------------------------------

## 7 · Package Version Dependency Note

AutoDeskR v0.4.0 requires **R ≥ 4.1.0** and depends on: - `httr2` — HTTP requests - `jsonlite` — JSON parsing - `curl` — file transfers - `shiny` — viewer embedding

Any new functions added for §3 should follow the same `httr2`-based `aps_request()` / `aps_perform()` internal helper pattern already established in the package source.

------------------------------------------------------------------------

## 8 · Strategic Vision — *BIM and CAD Analytics in R*

### 7.0 Scope Boundary

*R and the AutoDesk Platform* stays tightly scoped to **BIM and CAD data** — the file formats, model structures, geometry, and cloud APIs that architects, engineers, and BIM managers work with daily. This means the expansion adds depth in areas directly connected to design files and building models, not general AEC analytics (no structural FEA, geotechnical logs, energy simulation, or project controls).

The guiding test for any new chapter: *does it require a BIM model or CAD file as its primary input or output?* If yes, it belongs here.

------------------------------------------------------------------------

### 7.1 Title Transition Plan

| Phase | Title | Status |
|----|----|----|
| ~~**Previous**~~ | ~~*R and the AutoDesk Platform*~~ | ~~AutoDeskR / APS focused~~ |
| ~~**Near-term**~~ | ~~*R and the AutoDesk Platform: BIM & CAD Analytics*~~ | ~~Skipped~~ |
| **Now (current)** | *BIM and CAD Analytics in R* | Triggered — non-APS content (3D Geometry, DWG Analytics, Digital Twins) exceeds 40 % of chapters |

------------------------------------------------------------------------

### 7.2 New Content Areas

Each area below is a proposed new **Part** in the expanded book structure. All content is gated to BIM/CAD inputs or outputs.

#### Part B — 3D Geometry & Mesh Analysis

Once a CAD file is translated to OBJ or STL via the Model Derivative API, the resulting mesh can be analysed and visualised in R.

| Chapter | Key packages | Topics |
|----|----|----|
| Reading OBJ and STL meshes | `rgl`, `Rvcg` | Importing translated AutoDeskR outputs |
| Mesh metrics | `Rvcg`, `geometry` | Surface area, volume, bounding box, centroid |
| 3D visualisation | `rgl`, `rayshader` | Interactive 3D plots, rendered images |
| Point cloud analysis | AutoDeskR + `lidR` | Reality Capture output → point cloud metrics |
| Mesh comparison | `Rvcg` | Comparing as-designed vs as-built meshes |

#### Part C — DWG / DXF Layer Analytics

DWG and DXF files expose rich layer and attribute data. After translation via the Model Derivative API, `getData()` returns a structured property set that can be analysed directly.

| Chapter | Key packages | Topics |
|----|----|----|
| Layer structure analysis | AutoDeskR, `dplyr` | Parsing `getData()` output by layer; area and count by layer |
| Attribute extraction | AutoDeskR, `dplyr` | Custom properties, block attributes |
| Cross-drawing comparison | AutoDeskR, `dplyr` | Comparing layer sets across multiple DWG uploads |
| Automated drawing reports | AutoDeskR, `gt`, `quarto` | Parameterised Quarto reports from DWG metadata |

#### Part E — Digital Twins (BIM-Linked)

A digital twin links a BIM model to live operational data (sensors, meters, IoT). This part stays scoped to the model side — linking APS viewer output to time-series data streams, not general IoT infrastructure.

| Chapter | Key packages | Topics |
|----|----|----|
| AutoDesk Tandem overview | AutoDeskR (planned) | Tandem API concepts; twin vs BIM model |
| Linking sensor streams to model elements | `httr2`, AutoDeskR | Fetching readings keyed to `objectId` |
| Live dashboards | `shiny`, `dygraphs` | Time-series + 3D viewer side-by-side |

------------------------------------------------------------------------

### 7.3 Proposed Expanded Book Structure

``` yaml
parts:
  - "Front Matter"            # existing
  - "Core APIs"               # existing
  - "Project & Account APIs"  # existing
  - "3D Geometry & Meshes"    # implemented §7.2B
  - "DWG & DXF Analytics"     # implemented §7.2C
  - "Digital Twins"           # implemented §7.2E (Tandem REST API via httr2)
  - "Reference"               # existing
```

------------------------------------------------------------------------

### 7.4 Additional Package Dependencies to Add

| Package | CRAN? | Purpose | Status |
|----|----|----|----|
| `rgl` | ✅ | Interactive 3D visualisation | Implemented (Part B) |
| `Rvcg` | ✅ | Mesh processing (area, volume, comparison) | Implemented (Part B) |
| `geometry` | ✅ | Computational geometry primitives | Implemented (Part B) |
| `rayshader` | ✅ | High-quality 3D rendered images | Implemented (Part B) |
| `lidR` | ✅ | Point cloud analysis from Reality Capture output | Implemented (Part B) |
| `gt` | ✅ | Publication-quality tables for reports | Implemented (Part C) |
| `dygraphs` | ✅ | Interactive time-series plots for digital twin dashboards | Implemented (Part E) |

------------------------------------------------------------------------

### 7.5 Prerequisite Before Expanding

Complete §3 (ACC Data Management, Webhooks, Issues, Account Admin) first so that the BIM coordination and digital twin chapters have working API foundations to build on. The §7 expansion deepens BIM/CAD coverage; it does not widen the subject domain.
