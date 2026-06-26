"""Structural EPUB validity via W3C epubcheck (v5.3.0). Skips when epubcheck is
unavailable (local dev); CI installs it and sets EPUBCHECK_JAR. Catches
mimetype/OPF/spine errors — and image/media-type mismatches (PKG-021) — that
byte-equality goldens cannot.

Uses a REAL (stdlib-generated) PNG: epubcheck decodes embedded images, so fake
image bytes are (correctly) rejected as corrupt.
"""
import os, shutil, struct, subprocess, sys, tempfile, unittest, zlib
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_epub  # noqa: E402


def _png_1x1():
    def chunk(typ, data):
        body = typ + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)   # 1x1, 8-bit, RGB
    idat = zlib.compress(b"\x00\xff\x00\x00")              # filter byte + one red pixel
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _canon():
    return {
        "source_url": "https://x.com/q/status/100", "tweet_id": "100",
        "author_name": "Quant", "handle": "q",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "Tweet one $AAPL +12.5%.", "media": [],
        "provider": "manual", "captured_at": "2026-06-26T00:00:00Z",
        "provenance": {"thread_completeness": "2 of 2",
                       "capture_method": "manual paste, x-study v0.2",
                       "captured_at": "2026-06-26T00:00:00Z",
                       "capture_scope": "Excludes: quoted tweets, video/GIF media."},
        "thread_items": [
            {"index": 1, "text": "Tweet one $AAPL +12.5%.", "url": "https://x.com/q/status/100",
             "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "posted_at_utc": "2026-06-24T11:52:51Z",
             "media": [{"type": "photo", "url": "x", "local_path": "images/img1.png"}]},
            {"index": 2, "text": "Tweet two.\n\nRow1   100\nRow2   200",
             "url": "https://x.com/q/status/101", "posted_at": None, "posted_at_utc": None,
             "media": [{"type": "photo", "url": "y", "local_path": "images/img2.png"}]},
        ],
    }


def _epubcheck_cmd():
    jar = os.environ.get("EPUBCHECK_JAR")
    if jar and os.path.exists(jar) and shutil.which("java"):
        return ["java", "-jar", jar]
    if shutil.which("epubcheck"):
        return ["epubcheck"]
    return None


class TestEpubcheck(unittest.TestCase):
    def test_thread_epub_is_valid(self):
        cmd = _epubcheck_cmd()
        if not cmd:
            self.skipTest("epubcheck/java not available (CI installs it)")
        enrich = {"title": "Quant - Thread",
                  "alt_texts": {"images/img1.png": "Chart A", "images/img2.png": "Chart B"}}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "images"))
            for n in (1, 2):
                with open(os.path.join(d, "images", f"img{n}.png"), "wb") as f:
                    f.write(_png_1x1())
            out = os.path.join(d, "thread.epub")
            build_epub.build(_canon(), out, img_dir=d, enrichment=enrich)
            r = subprocess.run(cmd + [out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"epubcheck failed:\n{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main()
