# x-study

Archive an X (Twitter) post **or multi-tweet thread** as a faithful **md / epub / pdf** document with embedded images.

## Usage
Give Claude an X post URL — e.g. `x study https://x.com/<user>/status/<id>` (or `x 포스트 저장 <URL>`).
For a **thread**, say "x thread" / "save this thread" and paste all tweets in order in one message
(separated by a line with only `---`) — Claude assembles them, echoes the result for confirmation, then builds.
Output: `{handle}_{slug}_{YYYY-MM-DD}.{ext}` in your download path (default `~/Downloads/`).

## Configuration
MEMORY.md `## X Study Settings` (format, download path). `tag` is asked each run.

## Dependencies
- **md / epub**: `python3` on PATH (standard library only — no pip packages).
- **pdf**: optional — `pandoc` + a PDF engine (`weasyprint`, `wkhtmltopdf`, or `typst`). Without them, x-study saves md/epub and prints an install command.
- **Windows**: the workflow runs shell + `python3` commands — use **WSL** or **Git Bash** (same as yt-study).

## How it works
A SKILL.md orchestrates: `fetch_post.py` (fxtwitter/vxtwitter → canonical JSON; manual-paste fallback),
`download_media.py` (photos from `pbs.twimg.com`, per-item SSRF guard), Claude writes an analytical title +
descriptive alt text to `enrichment.json`, then `build_md.py` / `build_epub.py` render the document from the
**same** inputs (so md and epub stay in lockstep and are byte-reproducible). `build_pdf.py` converts the md
via pandoc.

## Threads
Free mirror APIs expose only a tweet's *parent* (no sibling/child list), so a full thread can't be
auto-collected. x-study therefore archives threads by **manual paste** — the only free way to guarantee
completeness. Each tweet becomes its own block with its chart directly beneath it (chart↔claim attribution),
and the document carries a **completeness banner** + **provenance** ("N of M" — M is `unverified` unless you
confirm the thread is complete — plus per-tweet permalink + UTC timestamp) so the archive stays citable and
honest about any gaps. Single posts are unchanged (no banner, no provenance).

## Privacy & limits
Uses public mirror APIs (fxtwitter/vxtwitter); no login or API key. Personal archiving of public posts —
respect [X's Terms of Service](https://x.com/en/tos). Long-form note tweets are captured in full; if a post
looks truncated you'll be asked to paste it. Videos/GIFs are saved as links, not embedded; quote posts are
not structured-captured.

Privacy: the public post URL is sent to third-party mirror APIs (fxtwitter/vxtwitter) — no login, but review their terms if that matters.
