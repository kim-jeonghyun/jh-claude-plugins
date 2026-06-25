#!/usr/bin/env python3
"""Acquire an X post and emit canonical archive JSON (stdlib only).

Usage: python3 fetch_post.py <x_post_url> [--raw-dir DIR]
Providers tried in order: fxtwitter, vxtwitter.
Success: prints canonical JSON to stdout, exit 0.
Failure: prints {"error": "..."} to stderr, exit 2 (caller falls back to
structured manual paste at the SKILL.md level).
"""
import argparse, html, json, os, re, sys, urllib.request
from datetime import datetime, timezone

USER_AGENT = "Mozilla/5.0 (x-study)"
URL_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/([A-Za-z0-9_]+)/status/(\d+)")
PROVIDERS = [("fxtwitter", "https://api.fxtwitter.com"),
             ("vxtwitter", "https://api.vxtwitter.com")]

def parse_url(url):
    m = URL_RE.search((url or "").strip())
    if not m:
        raise ValueError(f"Not a valid X/Twitter status URL: {url!r}")
    return m.group(1), m.group(2)

def looks_truncated(text):
    # Fail-safe: only the ellipsis CHARACTER (…) or an explicit "Show more"
    # indicates truncation. Bare three dots ("...") are common in normal prose
    # and would false-positive, needlessly forcing a manual paste.
    t = (text or "").rstrip()
    return t.endswith("…") or "Show more" in t

def normalize_fxlike(raw_text, handle, tweet_id):
    data = json.loads(raw_text)
    t = data.get("tweet") or {}
    author = t.get("author") or {}
    media_obj = t.get("media") or {}
    # Capture ALL media (photos AND videos/GIFs). fxtwitter exposes the full
    # list under media.all; fall back to media.photos (all typed "photo").
    if media_obj.get("all"):
        media = [
            {"type": item.get("type") or "photo", "url": item.get("url"),
             "local_path": None, "width": item.get("width"), "height": item.get("height")}
            for item in media_obj["all"] if item.get("url")
        ]
    else:
        media = [
            {"type": "photo", "url": p.get("url"), "local_path": None,
             "width": p.get("width"), "height": p.get("height")}
            for p in (media_obj.get("photos") or []) if p.get("url")
        ]
    return {
        "source_url": t.get("url") or f"https://x.com/{handle}/status/{tweet_id}",
        "tweet_id": tweet_id,
        "author_name": author.get("name") or handle,
        "handle": author.get("screen_name") or handle,
        "posted_at": t.get("created_at"),
        "lang": t.get("lang") or "en",
        "text": html.unescape(t.get("text") or ""),
        "expanded_urls": [],
        "media": media,
        "quote_post": None,
        "thread_items": [],
        "provider": None,
        "raw_provider_ref": None,
        "captured_at": None,
        "truncated": False,
        "tags": [],
    }

def _http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        # Strict decode: invalid bytes raise UnicodeDecodeError rather than
        # silently producing mojibake. The provider loop catches it, falls
        # through to the next mirror, and ultimately to the manual-paste path.
        return r.read().decode("utf-8")

def fetch(url, raw_dir=None):
    handle, tweet_id = parse_url(url)
    last_err = None
    for name, base in PROVIDERS:
        try:
            raw = _http_get(f"{base}/{handle}/status/{tweet_id}")
            canon = normalize_fxlike(raw, handle, tweet_id)
            canon["provider"] = name
            canon["truncated"] = looks_truncated(canon["text"])
            if raw_dir:
                os.makedirs(os.path.join(raw_dir, "raw"), exist_ok=True)
                ref = os.path.join("raw", f"{tweet_id}.{name}.json")
                with open(os.path.join(raw_dir, ref), "w", encoding="utf-8") as f:
                    f.write(raw)
                canon["raw_provider_ref"] = ref
            if canon["truncated"]:
                last_err = f"{name}: text looks truncated"
                continue
            canon["captured_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            return canon
        except Exception as e:  # noqa: BLE001 - any provider failure -> next
            last_err = f"{name}: {e}"
            continue
    raise RuntimeError(last_err or "all providers failed")

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--raw-dir", default=None)
    args = ap.parse_args(argv)
    try:
        canon = fetch(args.url, args.raw_dir)
    except Exception as e:  # noqa: BLE001
        json.dump({"error": str(e)}, sys.stderr)
        return 2
    json.dump(canon, sys.stdout, ensure_ascii=False, indent=2)
    return 0

if __name__ == "__main__":
    sys.exit(main())
