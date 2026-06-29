# Changelog

All notable changes to this project's plugins are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
This is the **authoritative source** for version history. GitHub Releases link here.

## [Unreleased]

### Added
- **x-study** plugin v0.1.0 — archive an X (Twitter) post as a faithful md/epub/pdf with embedded images (mirror-API fetch via fxtwitter/vxtwitter, stdlib EPUB builder, optional pandoc PDF; SSRF-guarded media download).

## [x-study v0.2.1] - 2026-06-28

### Added
- **Per-format download paths**: `## X Study Settings` now accepts optional `Download path (md)` / `Download path (epub)` / `Download path (pdf)` overrides (resolution: per-format → general `Download path` → `~/Downloads/`). Lets `md` go to an Obsidian vault while `epub`/`pdf` archive elsewhere. PDF now builds its intermediate markdown in the work dir (not the saved md path).

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

## [yt-study v1.1.1] - 2026-06-29

### Fixed
- **Silent subtitle failure**: `extract_transcript.sh` relied on yt-dlp's exit code, which is `0` even when no subtitle exists — so "no subtitles" was treated as success and produced an empty transcript. Success is now detected by an actual output file.

### Changed
- Subtitle priority refined and tried one-at-a-time in strict order: manual `ko-orig > ko > en` → auto `ko-orig > ko > en` (adds YouTube's "Korean (Original)" track, preferred over the sometimes machine-translated `ko`).
- Use `--convert-subs srt` (download native VTT → convert via ffmpeg) instead of `--sub-format srt`; modern yt-dlp flag names; clear stale outputs before detection; if SRT conversion fails (no ffmpeg) keep the VTT with a warning instead of losing it. Glob-based (not `ls`) file detection — shellcheck-clean and safe with spaces in the output path.

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
