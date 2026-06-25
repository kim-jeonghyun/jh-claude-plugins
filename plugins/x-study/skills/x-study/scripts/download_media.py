#!/usr/bin/env python3
"""Download canonical-JSON photos to local files (stdlib only).

Usage: python3 download_media.py <canonical.json> <out_dir>
Writes images/imgN.jpg under out_dir, updates media[].local_path, prints the
updated canonical JSON to stdout. Photos only; pbs.twimg.com only; redirects
disabled and final host validated (SSRF guard).
"""
import argparse, json, os, sys, urllib.parse, urllib.request

USER_AGENT = "Mozilla/5.0 (x-study)"
MAX_BYTES = 25 * 1024 * 1024  # 25 MB cap

def is_allowed_host(url):
    try:
        return urllib.parse.urlparse(url).hostname == "pbs.twimg.com"
    except Exception:
        return False

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None  # block 30x redirects entirely

_OPENER = urllib.request.build_opener(_NoRedirect)

def _fetch_bytes(url, timeout=30):
    if not is_allowed_host(url):
        raise ValueError("host not allowed")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with _OPENER.open(req, timeout=timeout) as r:
        if not is_allowed_host(r.geturl()):
            raise ValueError("redirected off allowlist")
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("image exceeds size cap")
    return data

def download_all(canon, out_dir):
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    idx = 0
    for m in canon.get("media", []):
        if m.get("type", "photo") != "photo":
            continue  # videos/GIFs referenced as links, not downloaded
        url = m.get("url")
        if not url or not is_allowed_host(url):
            continue
        idx += 1
        name = f"img{idx}.jpg"
        try:
            data = _fetch_bytes(url)
            with open(os.path.join(img_dir, name), "wb") as f:
                f.write(data)
            m["local_path"] = f"images/{name}"
        except Exception as e:  # noqa: BLE001 - keep link on failure
            sys.stderr.write(f"warn: image {idx} failed: {e}\n")
            m["local_path"] = None
    return canon

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("canonical_json")
    ap.add_argument("out_dir")
    args = ap.parse_args(argv)
    with open(args.canonical_json, encoding="utf-8") as f:
        canon = json.load(f)
    canon = download_all(canon, args.out_dir)
    json.dump(canon, sys.stdout, ensure_ascii=False, indent=2)
    return 0

if __name__ == "__main__":
    sys.exit(main())
