"""Golden-file regression for the deterministic text artifacts (md + EPUB chapter
+ OPF). Binary .epub byte-determinism is proven separately by the build-twice
filecmp test; these goldens lock the rendered CONTENT and are diffable in PRs.

Regenerate intentionally with:  UPDATE_GOLDEN=1 python3 tests/test_golden.py
"""
import os, sys, unittest
HERE = os.path.dirname(__file__)
GOLD = os.path.join(HERE, "golden")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_epub, build_md  # noqa: E402

ENRICH = {"title": "Quant - Q2 Macro Thread",
          "alt_texts": {"images/img1.jpg": "S&P 500 weekly chart", "images/img2.jpg": "Yield curve"},
          "tags": ["macro", "risk"]}

def fixture():
    return {
        "source_url": "https://x.com/quant/status/1000", "tweet_id": "1000",
        "author_name": "Quant", "handle": "quant",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "1/ Macro setup for $AAPL & $TSLA — P/E ≤ 15.", "media": [],
        "provider": "manual", "captured_at": "2026-06-26T11:50:00Z",
        "provenance": {
            "source_url": "https://x.com/quant/status/1000",
            "captured_at": "2026-06-26T11:50:00Z",
            "capture_method": "manual paste, x-study v0.2",
            "thread_completeness": "2 of 2",
            "capture_scope": "Excludes: quoted tweets, video/GIF media, expanded-URL resolution, replies by other users.",
        },
        "thread_items": [
            {"index": 1, "text": "1/ Macro setup for $AAPL & $TSLA — P/E ≤ 15.",
             "url": "https://x.com/quant/status/1000",
             "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "posted_at_utc": "2026-06-24T11:52:51Z",
             "media": [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}]},
            {"index": 2, "text": "2/ Returns:\nAAPL   +12.5%\nTSLA   −5.3%",
             "url": "https://x.com/quant/status/1001",
             "posted_at": "Wed Jun 24 12:01:00 +0000 2026", "posted_at_utc": "2026-06-24T12:01:00Z",
             "media": [{"type": "photo", "url": "y", "local_path": "images/img2.jpg"}]},
        ],
    }

class TestGolden(unittest.TestCase):
    def _check(self, name, actual):
        path = os.path.join(GOLD, name)
        if os.environ.get("UPDATE_GOLDEN"):
            os.makedirs(GOLD, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(actual)
            self.skipTest(f"regenerated {name}")
        with open(path, encoding="utf-8") as f:
            expected = f.read()
        self.assertEqual(actual, expected, f"{name} drift — regenerate with UPDATE_GOLDEN=1 if intended")

    def test_md_golden(self):
        self._check("thread.md", build_md.render(fixture(), ENRICH))

    def test_chapter_golden(self):
        self._check("thread.chapter.xhtml",
                    build_epub._thread_chapter(fixture(), ENRICH["title"], ENRICH["alt_texts"]))

    def test_opf_golden(self):
        self._check("thread.opf", build_epub._opf(fixture(), ENRICH["title"]))


if __name__ == "__main__":
    unittest.main()
