#!/usr/bin/env python3
"""Build faithful, deterministic Markdown from canonical JSON + enrichment.json.

Usage: python3 build_md.py <canonical.json> <out.md> [--enrichment FILE]

Same inputs as build_epub.py, so md and epub stay in lockstep (parity) and the
output is byte-reproducible (a pure function of the inputs — no wall-clock).
Single tweet (thread_items == []): front-matter + body + media + source.
Thread (thread_items non-empty): + a completeness banner + one block per tweet,
each chart directly under its owning tweet (chart<->claim attribution).

Untrusted tweet text/urls/alt are archived as LITERAL text: entity-encode &,<,>
then backslash-escape markdown-active punctuation, size code fences past any
embedded backticks, and scheme-allowlist + percent-encode every link target —
so a crafted tweet can't inject markup/links into the md or the pandoc PDF.
"""
import argparse, json, os, re, sys

_MD_INLINE = re.compile(r"([\\`*_\[\]])")          # inline emphasis/code/link/escape chars
_MD_LEAD = re.compile(r"^(\s*)([#>|+\-])")          # leading block triggers (not in inline set)
_MD_OL = re.compile(r"^(\s*)(\d{1,9})([.)])(\s|$)")  # ordered-list "1." / "1)"

def esc(s):
    # Entity-encode &,<,> so untrusted text is never raw HTML in the md (and so it
    # survives pandoc->PDF as visible text, not a dropped HTML block).
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _md_inline(s):
    # Backslash-escape inline emphasis/code/link metacharacters (for link labels,
    # image alt, and as the first pass of full-line escaping).
    return _MD_INLINE.sub(r"\\\1", str(s or ""))

def _md_line(line):
    # Full-line escape: inline metachars + leading block triggers, so financial
    # notation ($BRK_A, 3*2, leading "- 5%", "> 50%", "# 1 pick") is archived verbatim.
    line = _md_inline(line)
    line = _MD_OL.sub(r"\1\2\\\3\4", line)
    line = _MD_LEAD.sub(r"\1\\\2", line)
    return line

def _yaml(s):
    s = str(s if s is not None else "").replace("\\", "\\\\").replace('"', '\\"')
    s = re.sub(r"[\r\n\t]", " ", s)   # no control chars inside a flow scalar
    return '"' + s + '"'

def _is_safe_local(lp):
    if not lp or lp.startswith("/"):
        return False
    parts = lp.replace("\\", "/").split("/")
    return parts[0] == "images" and ".." not in parts and ":" not in parts[0]

def _safe_url(u):
    # Only web/mail schemes may become a link target; percent-encode the chars
    # that would break out of `](...)`. Returns "" if the scheme is not allowed.
    u = str(u or "")
    if not u.lower().startswith(("http://", "https://", "mailto:")):
        return ""
    return u.replace("(", "%28").replace(")", "%29").replace(" ", "%20")

def _safe_path(p):
    if not _is_safe_local(p):
        return ""
    return p.replace("(", "%28").replace(")", "%29").replace(" ", "%20")

def _link(label, url):
    # Angle-bracket autolink target tolerates the (already percent-encoded) URL;
    # falls back to plain escaped text when the scheme is disallowed.
    safe = _safe_url(url)
    text = _md_inline(esc(label))
    return f"[{text}](<{safe}>)" if safe else text

def _media_owners(canon):
    items = canon.get("thread_items")
    return items if items else [canon]

def _looks_tabular(block):
    # Same heuristic as build_epub: the column signal must repeat across >=2 lines.
    lines = [l for l in block.splitlines() if l.strip()]
    if len(lines) < 2:
        return False
    def sig(l):
        return ("\t" in l or re.match(r"\s{2,}\S", l) is not None
                or l.lstrip().startswith("|") or re.search(r"\S {2,}\S", l) is not None)
    return sum(1 for l in lines if sig(l)) >= 2

def _render_text(text):
    out = []
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        block = block.strip("\n")
        if not block.strip():
            continue
        if _looks_tabular(block):
            # fence longer than any backtick run inside -> embedded ``` can't break out
            longest = max((len(m) for m in re.findall(r"`+", block)), default=0)
            fence = "`" * max(3, longest + 1)
            out.append(f"{fence}\n{block}\n{fence}")
        else:
            # entity-encode, escape md punctuation, join with a hard break ("  \n")
            # so intra-block line structure matches the EPUB's <br/> (parity).
            out.append("  \n".join(_md_line(esc(line)) for line in block.split("\n")))
    return "\n\n".join(out)

def _media_lines(media, alts):
    lines = []
    for m in media:
        lp = m.get("local_path")
        if lp and _is_safe_local(lp):
            lines.append(f"![{_md_inline(esc(alts.get(lp, '')))}]({_safe_path(lp)})")
        elif m.get("url"):
            safe = _safe_url(m["url"])
            if safe:
                lines.append(f"[media not embedded — view original](<{safe}>)")
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
        f"# {_md_inline(esc(canon.get('author_name')))} (@{_md_inline(esc(canon.get('handle')))})",
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
            link, posted = item.get("url") or "", item.get("posted_at") or item.get("posted_at_utc") or ""
            meta = " · ".join(x for x in [_link(link, link) if link else "", esc(posted)] if x)
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
    src = _safe_url(canon.get("source_url"))
    src_render = f"<{src}>" if src else esc(canon.get("source_url"))
    out += ["---", f"Source: {src_render} · captured {esc(canon.get('captured_at'))} · via {esc(canon.get('provider'))}"]
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
