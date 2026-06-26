#!/usr/bin/env python3
"""Build faithful, deterministic Markdown from canonical JSON + enrichment.json.

Usage: python3 build_md.py <canonical.json> <out.md> [--enrichment FILE]

Same inputs as build_epub.py, so md and epub stay in lockstep (parity) and the
output is byte-reproducible (a pure function of the inputs — no wall-clock).
Single tweet (thread_items == []): front-matter + body + media + source.
Thread (thread_items non-empty): + a completeness banner + one block per tweet,
each chart directly under its owning tweet (chart<->claim attribution).
"""
import argparse, json, os, re, sys

def esc(s):
    # Entity-encode &,<,> so untrusted tweet text is never raw HTML in the md
    # (and so it survives pandoc->PDF as visible text, not a dropped HTML block).
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _yaml(s):
    return '"' + str(s if s is not None else "").replace("\\", "\\\\").replace('"', '\\"') + '"'

def _media_owners(canon):
    items = canon.get("thread_items")
    return items if items else [canon]

def _looks_tabular(block):
    for line in block.splitlines():
        if "\t" in line or re.search(r"\S {2,}\S", line):
            return True
    return False

def _render_text(text):
    out = []
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        block = block.strip("\n")
        if not block.strip():
            continue
        if _looks_tabular(block):
            # fenced code preserves column alignment exactly; content inside a
            # code fence is literal (never parsed as HTML/markdown), so it is
            # safe to emit raw — entity-encoding would corrupt the display.
            out.append("```\n" + block + "\n```")
        else:
            out.append(esc(block))
    return "\n\n".join(out)

def _media_lines(media, alts):
    lines = []
    for m in media:
        lp = m.get("local_path")
        if lp:
            lines.append(f"![{esc(alts.get(lp, ''))}]({lp})")
        elif m.get("url"):
            lines.append(f"[media not embedded — view original]({m['url']})")
    return lines

def render(canon, enrichment=None):
    enrichment = enrichment or {}
    title = enrichment.get("title") or f"{canon.get('author_name') or canon.get('handle')} - X Post"
    alts = enrichment.get("alt_texts") or {}
    tags = enrichment.get("tags") or []
    out = [
        "---",
        f"title: {_yaml(title)}",
        f"url: {_yaml(canon.get('source_url'))}",
        f"author: {_yaml(canon.get('author_name'))}",
        f"handle: {_yaml(canon.get('handle'))}",
        f"posted_at: {_yaml(canon.get('posted_at'))}",
        f"processed_at: {_yaml(canon.get('captured_at'))}",
        "type: x-post",
        "tags: [" + ", ".join(_yaml(t) for t in tags) + "]",
        "---",
        "",
        f"# {esc(canon.get('author_name'))} (@{esc(canon.get('handle'))})",
        "",
    ]
    prov = canon.get("provenance") or {}
    items = canon.get("thread_items")
    if items:
        if prov:
            out.append(
                f"> **Archive note:** {esc(prov.get('thread_completeness') or 'unverified')} tweets "
                "captured by manual paste. Tweets posted after the last pasted tweet cannot be "
                f"detected by the free mirror API. {esc(prov.get('capture_scope') or '')}".rstrip()
            )
            out.append("")
        total = len(items)
        for i, item in enumerate(items, 1):
            out.append(f"## Captured tweet {i} of {total}")
            link = item.get("url") or ""
            posted = item.get("posted_at") or item.get("posted_at_utc") or ""
            meta = " · ".join(x for x in [f"[{link}]({link})" if link else "", esc(posted)] if x)
            if meta:
                out.append(f"*{meta}*")
            out.append("")
            txt = _render_text(item.get("text"))
            if txt:
                out += [txt, ""]
            for line in _media_lines(item.get("media", []), alts):
                out += [line, ""]
    else:
        out.append(f"*Posted: {esc(canon.get('posted_at'))} · {esc(canon.get('provider'))}*")
        out.append("")
        txt = _render_text(canon.get("text"))
        if txt:
            out += [txt, ""]
        for line in _media_lines(canon.get("media", []), alts):
            out += [line, ""]
    src = canon.get("source_url") or ""
    out += ["---", f"Source: {src} · captured {esc(canon.get('captured_at'))} · via {esc(canon.get('provider'))}"]
    return "\n".join(out) + "\n"

def build(canon, out_path, enrichment=None):
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(canon, enrichment))
    return out_path

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("canonical_json")
    ap.add_argument("out_md")
    ap.add_argument("--enrichment", default=None)
    args = ap.parse_args(argv)
    with open(args.canonical_json, encoding="utf-8") as f:
        canon = json.load(f)
    enrichment = None
    if args.enrichment and os.path.exists(args.enrichment):
        with open(args.enrichment, encoding="utf-8") as f:
            enrichment = json.load(f)
    build(canon, args.out_md, enrichment)
    print(args.out_md)
    return 0

if __name__ == "__main__":
    sys.exit(main())
