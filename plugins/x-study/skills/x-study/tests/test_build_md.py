import filecmp, os, sys, tempfile, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_md  # noqa: E402

def single_canon():
    return {
        "source_url": "https://x.com/markminervini/status/2069750598728089949",
        "tweet_id": "2069750598728089949",
        "author_name": "Mark Minervini", "handle": "markminervini",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "Risk & reward with <b> $AAPL +12.5%.\n\nSecond paragraph.",
        "media": [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}],
        "provider": "fxtwitter", "captured_at": "2026-06-25T00:00:00Z", "thread_items": [],
    }

def thread_canon():
    return {
        "source_url": "https://x.com/q/status/100", "tweet_id": "100",
        "author_name": "Quant", "handle": "q",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "Tweet one $AAPL +12.5%.", "media": [],
        "provider": "manual", "captured_at": "2026-06-26T00:00:00Z",
        "provenance": {"thread_completeness": "2 of 2",
                       "capture_scope": "Excludes: quoted tweets, video/GIF media."},
        "thread_items": [
            {"index": 1, "text": "Tweet one $AAPL +12.5%.", "url": "https://x.com/q/status/100",
             "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "posted_at_utc": "2026-06-24T11:52:51Z",
             "media": [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}]},
            {"index": 2, "text": "Tweet two <script>alert(1)</script>\n\nRow1   100\nRow2   200",
             "url": "https://x.com/q/status/101", "posted_at": None, "posted_at_utc": None,
             "media": [{"type": "photo", "url": "y", "local_path": "images/img2.jpg"}]},
        ],
    }

class TestSingle(unittest.TestCase):
    def test_front_matter_and_body(self):
        md = build_md.render(single_canon(),
                             {"title": "Mark Minervini - Market Analysis",
                              "alt_texts": {"images/img1.jpg": "Bull Markets S&P 500 Chart"},
                              "tags": ["macro"]})
        self.assertTrue(md.startswith("---\n"))
        self.assertIn('title: "Mark Minervini - Market Analysis"', md)
        self.assertIn("tags: [\"macro\"]", md)
        self.assertIn("# Mark Minervini (@markminervini)", md)
        self.assertIn("*Posted: Wed Jun 24 11:52:51 +0000 2026 · fxtwitter*", md)
        self.assertIn("![Bull Markets S&amp;P 500 Chart](images/img1.jpg)", md)  # alt entity-encoded
        self.assertIn("Risk &amp; reward with &lt;b&gt; $AAPL +12.5%.", md)       # <,&,>,$,% faithful
        self.assertIn("Second paragraph.", md)
        self.assertIn("Source: <https://x.com/markminervini/status/2069750598728089949>", md)

class TestThread(unittest.TestCase):
    def test_banner_blocks_and_safety(self):
        md = build_md.render(thread_canon(),
                             {"title": "Quant - Thread",
                              "alt_texts": {"images/img1.jpg": "A", "images/img2.jpg": "B"}})
        self.assertIn("> **Archive note:** 2 of 2 tweets", md)            # completeness banner
        self.assertIn("Excludes: quoted tweets", md)                       # capture scope
        self.assertIn("## Captured tweet 1 of 2", md)
        self.assertIn("## Captured tweet 2 of 2", md)
        self.assertIn("https://x.com/q/status/101", md)                    # per-tweet permalink
        self.assertIn("$AAPL +12.5%", md)                                  # financial content
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", md)         # script escaped, never raw HTML
        self.assertNotIn("<script>alert", md)
        self.assertIn("```\nRow1   100\nRow2   200\n```", md)              # tabular -> fenced code
        self.assertIn("![B](images/img2.jpg)", md)                         # chart under its tweet

class TestMarkdownSafety(unittest.TestCase):
    """Untrusted tweet text/urls/alt must be archived as literal text — no markdown
    or link injection into the md or the downstream pandoc PDF."""

    def _single(self, text, media=None):
        return {"source_url": "https://x.com/q/status/1", "tweet_id": "1",
                "author_name": "Q", "handle": "q", "posted_at": None, "lang": "en",
                "text": text, "media": media or [], "provider": "manual",
                "captured_at": "2026-06-26T00:00:00Z", "thread_items": []}

    def test_code_fence_breakout_blocked(self):
        # a tabular tweet whose text contains ``` must not close the fence early
        text = "A   1\n```\n## INJECTED\nB   2"
        md = build_md.render(self._single(text), {})
        self.assertIn("````\n", md)               # opening fence widened to 4 backticks
        self.assertGreaterEqual(md.count("````"), 2)            # opening + closing 4-fence
        self.assertIn("## INJECTED", md.split("````")[1])       # heading sits INSIDE the fence

    def test_link_target_breakout_blocked(self):
        # a media url containing ")" must not break out of the markdown link
        media = [{"type": "video", "url": "https://x.com/a)b [evil](javascript:alert(1))", "local_path": None}]
        md = build_md.render(self._single("hi", media), {})
        self.assertNotIn("[evil](javascript:alert(1))", md)
        self.assertNotIn("](javascript:", md)

    def test_disallowed_scheme_dropped(self):
        media = [{"type": "video", "url": "javascript:alert(1)", "local_path": None}]
        md = build_md.render(self._single("hi", media), {})
        self.assertNotIn("javascript:", md)

    def test_alt_metachars_escaped(self):
        media = [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}]
        md = build_md.render(self._single("hi", media),
                             {"alt_texts": {"images/img1.jpg": "chart] then [x"}})
        self.assertIn("\\]", md)                  # "]" escaped -> can't close the image early
        self.assertIn("\\[x", md)                 # "[" escaped
        self.assertNotIn("chart] then [x", md)    # raw (unescaped) alt not present

    def test_prose_active_chars_escaped(self):
        md = build_md.render(self._single("- 5% drawdown\n\n> 50% odds\n\nuse value_investing or 3*2"), {})
        self.assertIn("\\- 5% drawdown", md)     # leading "-" backslash-escaped (not a bullet)
        self.assertIn("&gt; 50% odds", md)       # leading ">" entity-encoded (not a blockquote)
        self.assertIn("value\\_investing", md)   # "_" not emphasis
        self.assertIn("3\\*2", md)               # "*" not emphasis

    def test_hard_breaks_for_parity(self):
        md = build_md.render(self._single("line one\nline two\nline three"), {})
        self.assertIn("line one  \nline two  \nline three", md)  # markdown hard breaks

    def test_yaml_control_chars_neutralized(self):
        md = build_md.render(self._single("hi"), {"title": "ok\ninjected: pwned"})
        self.assertNotIn("\ninjected: pwned", md)        # newline did not create a YAML key
        self.assertIn('title: "ok injected: pwned"', md)  # collapsed to one scalar


class TestDeterminism(unittest.TestCase):
    def test_md_byte_identical(self):
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "a.md"); b = os.path.join(d, "b.md")
            build_md.build(thread_canon(), a, {"title": "T", "alt_texts": {}})
            build_md.build(thread_canon(), b, {"title": "T", "alt_texts": {}})
            self.assertTrue(filecmp.cmp(a, b, shallow=False), "md not byte-deterministic")

if __name__ == "__main__":
    unittest.main()
