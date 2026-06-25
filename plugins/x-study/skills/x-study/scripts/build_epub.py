#!/usr/bin/env python3
"""Build a faithful EPUB from canonical JSON + enrichment.json (stdlib only).

Usage: python3 build_epub.py <canonical.json> <out.epub> [--enrichment FILE] [--img-dir DIR]
mimetype is stored first/uncompressed; other entries deflated.
"""
import argparse, json, os, re, sys, zipfile

CSS = """body { font-family: Georgia, serif, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"; margin: 2em; line-height: 1.7; color: #222; }
h1 { font-size: 1.4em; color: #1a1a2e; border-bottom: 2px solid #ccc; padding-bottom: 0.5em; }
.meta { color: #666; font-size: 0.9em; margin-bottom: 1.5em; }
p { margin: 0.8em 0; }
.images img { width: 100%; max-width: 100%; height: auto; display: block; margin: 1em 0; border: 1px solid #ddd; }
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

def _chapter(canon, title, alts):
    paras = "\n".join(f"    <p>{esc(p)}</p>" for p in split_paragraphs(canon.get("text")))
    figs = []
    for m in canon.get("media", []):
        lp = m.get("local_path")
        if lp:
            figs.append(f'    <figure><img src="{esc(lp)}" alt="{esc(alts.get(lp, ""))}"/></figure>')
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

def _opf(canon, title):
    items = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>',
        '    <item id="css" href="style.css" media-type="text/css"/>',
    ]
    n = 0
    for m in canon.get("media", []):
        if m.get("local_path"):
            n += 1
            items.append(f'    <item id="img{n}" href="{esc(m["local_path"])}" media-type="image/jpeg"/>')
    manifest = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{esc(title)}</dc:title>
    <dc:creator>{esc(canon.get('author_name'))}</dc:creator>
    <dc:language>{esc(canon.get('lang') or 'en')}</dc:language>
    <dc:identifier id="uid">{esc(canon.get('handle'))}-{esc(canon.get('tweet_id'))}</dc:identifier>
    <dc:source>{esc(canon.get('source_url'))}</dc:source>
    <meta property="dcterms:modified">2026-01-01T00:00:00Z</meta>
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
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", CONTAINER, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", _opf(canon, title), compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", NAV.replace("{title}", esc(title)), compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/chapter1.xhtml", _chapter(canon, title, alts), compress_type=zipfile.ZIP_DEFLATED)
        base = img_dir or os.path.dirname(os.path.abspath(out_path))
        for m in canon.get("media", []):
            lp = m.get("local_path")
            if lp:
                src = os.path.join(base, lp)
                if os.path.exists(src):
                    with open(src, "rb") as f:
                        z.writestr(f"OEBPS/{lp}", f.read(), compress_type=zipfile.ZIP_DEFLATED)
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
