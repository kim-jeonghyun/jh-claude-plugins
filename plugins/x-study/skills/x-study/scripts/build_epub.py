#!/usr/bin/env python3
"""Build a faithful EPUB from canonical JSON + enrichment.json (stdlib only).

Usage: python3 build_epub.py <canonical.json> <out.epub> [--enrichment FILE] [--img-dir DIR]

Single tweet (thread_items == []): one chapter, unchanged from v0.1.
Thread (thread_items non-empty): a completeness banner + one <section> per tweet,
each chart directly beneath its owning tweet (chart<->claim attribution).

Builds are byte-reproducible: mimetype is stored first/uncompressed; every entry
uses a fixed ZipInfo date and is written in sorted order with ZIP_STORED (DEFLATE
output is not stable across zlib versions, which would make committed goldens flaky).
"""
import argparse, json, os, re, sys, zipfile
from datetime import datetime
from email.utils import parsedate_to_datetime

# Fixed DOS timestamp for every entry -> identical bytes on every run/platform.
EPUB_EPOCH = (1980, 1, 1, 12, 1, 0)

CSS = """body { font-family: Georgia, serif, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"; margin: 2em; line-height: 1.7; color: #222; }
h1 { font-size: 1.4em; color: #1a1a2e; border-bottom: 2px solid #ccc; padding-bottom: 0.5em; }
h2 { font-size: 1.05em; color: #444; margin-top: 1.6em; }
.meta { color: #666; font-size: 0.9em; margin-bottom: 1.5em; }
p { margin: 0.8em 0; }
pre.tabular { white-space: pre-wrap; font-family: "Menlo", "Consolas", monospace; font-size: 0.9em; background: #f6f6f6; padding: 0.6em; }
.images img, figure img { width: 100%; max-width: 100%; height: auto; display: block; margin: 1em 0; border: 1px solid #ddd; }
figcaption { font-size: 0.8em; color: #888; }
.completeness-banner { border: 1px solid #d9b310; background: #fff8e1; padding: 0.8em 1em; margin-bottom: 1.5em; font-size: 0.9em; }
.tweet { margin-bottom: 1.5em; padding-bottom: 1em; border-bottom: 1px solid #eee; }
.tweet-meta { color: #888; font-size: 0.8em; margin-bottom: 0.4em; }
.source { font-size: 0.85em; color: #888; margin-top: 2em; border-top: 1px solid #eee; padding-top: 0.5em; }
"""

def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))

def split_paragraphs(text):
    parts = re.split(r"\n+", (text or "").strip())
    return [p.strip() for p in parts if p.strip()]

def slugify(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:60] or "x-post"

def default_title(canon):
    return f"{canon.get('author_name') or canon.get('handle')} - X Post"

def _media_type(path):
    ext = os.path.splitext(path or "")[1].lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp"}.get(ext, "image/jpeg")

def _safe_href(url):
    # Only web/mail schemes survive into an href; a pasted javascript:/data: link
    # must not be clickable in the EPUB (esc() blocks attribute breakout, not the
    # scheme itself). Relative/anchor refs are left as-is.
    u = str(url or "")
    low = u.lower()
    if low.startswith(("http://", "https://", "mailto:", "#")) or (u and ":" not in u.split("/")[0]):
        return u
    return "#"

def _is_safe_local(lp):
    # Embeddable only as a normalized relative path under images/ (no absolute
    # path, no "..", no drive) — a malicious canonical JSON must not make the
    # builder read/package files outside the work dir.
    if not lp or lp.startswith("/"):
        return False
    parts = lp.replace("\\", "/").split("/")
    return parts[0] == "images" and ".." not in parts and ":" not in parts[0]

def _media_owners(canon):
    # Threads: thread_items is authoritative (top-level media ignored). Single
    # tweet: the root owns the media. Mirrors download_media._media_owners.
    items = canon.get("thread_items")
    return items if items else [canon]

def _embedded_images(canon):
    paths = []
    for owner in _media_owners(canon):
        for m in owner.get("media", []):
            lp = m.get("local_path")
            if lp and _is_safe_local(lp):
                paths.append(lp)
    return paths

# EPUB requires a dcterms:modified timestamp. Derive it deterministically from
# the post's own posted_at (Twitter format, e.g. "Wed Jun 24 11:52:51 +0000
# 2026"); fall back to a fixed value if missing/unparseable so builds stay
# reproducible (derived purely from input -- no wall-clock).
DCTERMS_FALLBACK = "2026-01-01T00:00:00Z"

def dcterms_modified(canon):
    posted = canon.get("posted_at")
    if posted:
        # RFC 2822 (Twitter "Wed Jun 24 11:52:51 +0000 2026")...
        try:
            return parsedate_to_datetime(posted).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:  # noqa: BLE001
            pass
        # ...or ISO-8601 (manual-paste threads may carry "2026-06-24T11:52:51Z")
        try:
            return datetime.fromisoformat(posted.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:  # noqa: BLE001 - unparseable -> deterministic fallback
            pass
    return DCTERMS_FALLBACK

# ---- single-tweet chapter (v0.1 behavior, unchanged) -----------------------

def _chapter(canon, title, alts):
    paras = "\n".join(f"    <p>{esc(p)}</p>" for p in split_paragraphs(canon.get("text")))
    figs = []
    for m in canon.get("media", []):
        lp = m.get("local_path")
        if lp and _is_safe_local(lp):
            figs.append(f'    <figure><img src="{esc(lp)}" alt="{esc(alts.get(lp, ""))}"/></figure>')
        elif m.get("url"):
            # Non-embedded media (failed photos, videos, GIFs): preserve a
            # visible link to the original source rather than dropping it.
            figs.append(f'    <figure><a href="{esc(_safe_href(m["url"]))}">[media not embedded — view original]</a></figure>')
    img_block = f'  <div class="images">\n' + "\n".join(figs) + "\n  </div>\n" if figs else ""
    meta, src = esc(canon.get("posted_at") or ""), esc(canon.get("source_url") or "")
    prov, cap = esc(canon.get("provider") or ""), esc(canon.get("captured_at") or "")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{esc(title)}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h1>{esc(canon.get('author_name'))} (@{esc(canon.get('handle'))})</h1>
  <div class="meta">Posted: {meta} · {prov}</div>
{paras}
{img_block}  <div class="source">Source: <a href="{src}">{src}</a> · captured {cap} · via {prov}</div>
</body>
</html>"""

# ---- thread chapter (per-tweet sections) -----------------------------------

def _looks_tabular(block):
    # A real table needs the column signal to REPEAT across >=2 lines; a single
    # line with "two spaces after a period" is prose, not a table. Signals: a tab,
    # a 2+ space leading indent, a pipe-delimited row, or 2+ spaces between
    # non-space chars (a column gap). Preserving alignment beats collapsing it:
    # financial tables must survive.
    lines = [l for l in block.splitlines() if l.strip()]
    if len(lines) < 2:
        return False
    def sig(l):
        return ("\t" in l or re.match(r"\s{2,}\S", l) is not None
                or l.lstrip().startswith("|") or re.search(r"\S {2,}\S", l) is not None)
    return sum(1 for l in lines if sig(l)) >= 2

def _render_text_blocks(text):
    out = []
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        block = block.strip("\n")
        if not block.strip():
            continue
        if _looks_tabular(block):
            out.append(f'    <pre class="tabular">{esc(block)}</pre>')
        else:
            inner = "<br/>".join(esc(line) for line in block.split("\n"))
            out.append(f"    <p>{inner}</p>")
    return "\n".join(out)

def _banner(prov):
    completeness = esc(prov.get("thread_completeness") or "unverified")
    scope = esc(prov.get("capture_scope") or "")
    return (
        '  <section class="completeness-banner" role="note">\n'
        f'    <p><strong>Archive note:</strong> {completeness} tweets captured by manual paste. '
        'Tweets posted after the last pasted tweet cannot be detected by the free mirror API. '
        f'{scope}</p>\n'
        '  </section>'
    )

def _tweet_section(item, i, total, alts):
    body = _render_text_blocks(item.get("text"))
    figs = []
    for m in item.get("media", []):
        lp = m.get("local_path")
        if lp and _is_safe_local(lp):
            figs.append(
                f'    <figure><img src="{esc(lp)}" alt="{esc(alts.get(lp, ""))}"/>'
                f'<figcaption>From captured tweet {i}</figcaption></figure>'
            )
        elif m.get("url"):
            figs.append(f'    <figure><a href="{esc(_safe_href(m["url"]))}">[media not embedded — view original]</a></figure>')
    raw_url = item.get("url") or ""
    permalink, href = esc(raw_url), esc(_safe_href(raw_url))
    posted = esc(item.get("posted_at") or item.get("posted_at_utc") or "")
    meta = f'<a href="{href}">{permalink}</a>' if permalink else ""
    if posted:
        meta = (meta + " · " if meta else "") + posted
    inner = [f'    <h2>Captured tweet {i} of {total}</h2>',
             f'    <div class="tweet-meta">{meta}</div>']
    if body:
        inner.append(body)
    if figs:
        inner.append("\n".join(figs))
    return (f'  <section epub:type="chapter" class="tweet" id="tweet{i}">\n'
            + "\n".join(inner) + "\n  </section>")

def _thread_chapter(canon, title, alts):
    items = canon.get("thread_items") or []
    total = len(items)
    prov = canon.get("provenance") or {}
    parts = []
    if prov:
        parts.append(_banner(prov))
    for i, item in enumerate(items, 1):
        parts.append(_tweet_section(item, i, total, alts))
    body = "\n".join(parts)
    src = esc(canon.get("source_url") or "")
    prov_name = esc(canon.get("provider") or "")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{esc(title)}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
  <h1>{esc(canon.get('author_name'))} (@{esc(canon.get('handle'))})</h1>
{body}
  <div class="source">Source: <a href="{src}">{src}</a> · via {prov_name}</div>
</body>
</html>"""

# ---- package / nav / container ---------------------------------------------

def _opf(canon, title):
    items = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>',
        '    <item id="css" href="style.css" media-type="text/css"/>',
    ]
    for n, lp in enumerate(_embedded_images(canon), 1):
        items.append(f'    <item id="img{n}" href="{esc(lp)}" media-type="{_media_type(lp)}"/>')
    manifest = "\n".join(items)
    prov = canon.get("provenance") or {}
    prov_meta = ""
    if prov:
        prov_meta = (
            f'\n    <meta property="dcterms:provenance">{esc(prov.get("capture_method", ""))}</meta>'
            f'\n    <meta property="dcterms:dateSubmitted">{esc(prov.get("captured_at", ""))}</meta>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{esc(title)}</dc:title>
    <dc:creator>{esc(canon.get('author_name'))}</dc:creator>
    <dc:language>{esc(canon.get('lang') or 'en')}</dc:language>
    <dc:identifier id="uid">{esc(canon.get('handle'))}-{esc(canon.get('tweet_id'))}</dc:identifier>
    <dc:source>{esc(canon.get('source_url'))}</dc:source>
    <meta property="dcterms:modified">{dcterms_modified(canon)}</meta>{prov_meta}
  </metadata>
  <manifest>
{manifest}
  </manifest>
  <spine>
    <itemref idref="nav"/>
    <itemref idref="chapter1"/>
  </spine>
</package>"""

NAV = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Table of Contents</title></head>
<body><nav epub:type="toc"><h1>Contents</h1>
<ol><li><a href="chapter1.xhtml">{title}</a></li></ol></nav></body></html>"""

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

def build(canon, out_path, img_dir=None, enrichment=None):
    enrichment = enrichment or {}
    title = enrichment.get("title") or default_title(canon)
    alts = enrichment.get("alt_texts") or {}
    chapter = _thread_chapter(canon, title, alts) if canon.get("thread_items") else _chapter(canon, title, alts)
    entries = {
        "META-INF/container.xml": CONTAINER,
        "OEBPS/content.opf": _opf(canon, title),
        "OEBPS/nav.xhtml": NAV.replace("{title}", esc(title)),
        "OEBPS/style.css": CSS,
        "OEBPS/chapter1.xhtml": chapter,
    }
    base = img_dir or os.path.dirname(os.path.abspath(out_path))
    for lp in _embedded_images(canon):
        src = os.path.join(base, lp)
        if os.path.exists(src):
            with open(src, "rb") as f:
                entries[f"OEBPS/{lp}"] = f.read()
    def _zi(name):
        # Pin every field that varies by platform so bytes are identical on
        # macOS/Linux/Windows: fixed date, Unix create_system, and rw-r--r-- perms
        # (external_attr=0 extracts as 000 -> "permission denied" in some readers).
        zi = zipfile.ZipInfo(name, date_time=EPUB_EPOCH)
        zi.create_system = 3
        zi.external_attr = 0o644 << 16
        return zi
    with zipfile.ZipFile(out_path, "w") as z:
        # mimetype first/stored (OCF); all entries STORED + sorted + fixed metadata
        # -> byte-reproducible across platforms (DEFLATE is not stable across zlib).
        z.writestr(_zi("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for name in sorted(entries):
            data = entries[name]
            if isinstance(data, str):
                data = data.encode("utf-8")
            z.writestr(_zi(name), data, compress_type=zipfile.ZIP_STORED)
    return out_path

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("canonical_json")
    ap.add_argument("out_epub")
    ap.add_argument("--enrichment", default=None)
    ap.add_argument("--img-dir", default=None)
    args = ap.parse_args(argv)
    with open(args.canonical_json, encoding="utf-8") as f:
        canon = json.load(f)
    enrichment = None
    if args.enrichment and os.path.exists(args.enrichment):
        with open(args.enrichment, encoding="utf-8") as f:
            enrichment = json.load(f)
    build(canon, args.out_epub, args.img_dir, enrichment)
    print(args.out_epub)
    return 0

if __name__ == "__main__":
    sys.exit(main())
