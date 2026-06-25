# x-study

Archive an X (Twitter) post as a faithful **md / epub / pdf** document with embedded images.

## Usage
Give Claude an X post URL: `x 포스트 저장 https://x.com/<user>/status/<id>`
Output: `{handle}_{slug}_{YYYY-MM-DD}.{ext}` in your download path (default `~/Downloads/`).

## Configuration
MEMORY.md `## X Study Settings` (format, download path). `tag` is asked each run.

## Dependencies
- **md / epub**: none (Python 3 standard library only).
- **pdf**: optional — `pandoc` + a PDF engine (`weasyprint`, `wkhtmltopdf`, or `typst`). Without them, x-study saves md/epub and prints an install command.

## How it works
A SKILL.md orchestrates: `fetch_post.py` (fxtwitter/vxtwitter → canonical JSON; manual-paste fallback), `download_media.py` (photos from pbs.twimg.com), Claude writes an analytical title + descriptive alt text to `enrichment.json`, then `build_epub.py` / `build_pdf.py` render the document.

## Privacy & limits
Uses public mirror APIs (fxtwitter/vxtwitter); no login or API key. Personal archiving. Photos are embedded; videos/GIFs are linked. Long-form posts come whole; multi-tweet threads are pasted manually in v1.
