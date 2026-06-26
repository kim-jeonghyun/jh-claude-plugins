# Changelog

All notable changes to this project's plugins are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
This is the **authoritative source** for version history. GitHub Releases link here.

## [Unreleased]

### Added
- **x-study** plugin v0.1.0 — archive an X (Twitter) post as a faithful md/epub/pdf with embedded images (mirror-API fetch via fxtwitter/vxtwitter, stdlib EPUB builder, optional pandoc PDF; SSRF-guarded media download).

## [x-study v0.2.0] - 2026-06-26

### Added
- **Multi-tweet thread archiving** (manual paste): per-tweet `<section>` blocks with each chart directly under its owning tweet (chart↔claim attribution), a completeness banner, and a provenance block ("N of M", capture-scope, per-tweet permalink + UTC) for citable, honest archives.
- `build_md.py` — deterministic Markdown builder consuming the same canonical + enrichment JSON as the EPUB builder, so md/epub stay in lockstep (parity) and md is golden-testable.
- Fidelity, golden-file, and epubcheck (v5.3.0 in CI) test suites; financial-content round-trip fixtures (`$AAPL`, `+12.5%`, `P/E ≤ 15`, `−5.3%` U+2212, `₿`, ASCII tables).

### Changed
- **EPUB builds are now byte-reproducible** (fixed `ZipInfo` dates + sorted entries + ZIP_STORED), so committed goldens are stable across platforms/zlib versions.
- `download_media.py` traverses every tweet's media with one global image counter and applies the `pbs.twimg.com` SSRF guard per item.
- `build_pdf.py` disables pandoc `tex_math_dollars` so cashtags (`$AAPL … $TSLA`) are never parsed as LaTeX math.
- Aligned/tabular tweet text renders in `<pre>` (EPUB) / fenced code (md) to preserve column alignment.

### Security
- Untrusted-content fence + plain-text output validation for the enrichment step; every field (incl. LLM title/alt) entity-encoded before XHTML/Markdown; personal-use disclaimer added.

## [yt-study v1.1.0] - 2026-03-09

### Changed
- Renamed from youtube-digest to yt-study
- Fork of team-attention/claude-plugins with full attribution

### Added
- Adaptive templates (SHORT/MEDIUM/LONG)
- Configurable output language
- Notion MCP direct integration support

## [article-study v0.2.0] - 2026-03-09

### Changed
- Renamed from blog-digest to article-study

### Added
- Deep research workflow reference
- Quiz patterns reference
- Configurable output language
