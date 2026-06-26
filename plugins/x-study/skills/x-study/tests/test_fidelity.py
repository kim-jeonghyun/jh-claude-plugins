"""Financial-content fidelity: numbers, %, $, math symbols, tables survive intact."""
import html, os, sys, unicodedata, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_epub, build_md  # noqa: E402

# Strings a quant thread must never corrupt.
FIXTURES = [
    "$AAPL", "+12.5%", "P/E ≤ 15", "−5.3%",  # U+2212 MINUS SIGN, not hyphen
    "₿", "Risk & reward", "<b>bold</b>", "x²", "100 < 200 > 50",
]
TABLE = "Ticker   Px     Chg\nAAPL     201.4  +1.2%\nTSLA     242.0  -3.4%"

class TestRoundTrip(unittest.TestCase):
    def test_unescape_of_escape_is_identity(self):
        # The property from plan §6.1: encoding then decoding returns the text.
        for s in FIXTURES + [TABLE]:
            self.assertEqual(html.unescape(build_epub.esc(s)), s, f"epub esc lost: {s!r}")
            self.assertEqual(html.unescape(build_md.esc(s)), s, f"md esc lost: {s!r}")

    def test_no_double_escape(self):
        self.assertEqual(build_epub.esc("Tom & Jerry"), "Tom &amp; Jerry")
        self.assertNotIn("&amp;amp;", build_epub.esc("Tom & Jerry"))
        self.assertNotIn("&amp;amp;", build_md.esc("A & B & C"))

    def test_no_unicode_normalization(self):
        # NFKC is destructive for financial glyphs (x² -> x2); we must NOT apply it.
        self.assertEqual(unicodedata.normalize("NFKC", "x²"), "x2")   # proves NFKC would corrupt
        self.assertEqual(html.unescape(build_epub.esc("x²")), "x²")    # we preserve it
        self.assertEqual(html.unescape(build_md.esc("x²")), "x²")

    def test_minus_sign_distinct_from_hyphen(self):
        self.assertEqual(html.unescape(build_epub.esc("−5.3%")), "−5.3%")
        self.assertNotEqual("−5.3%", "-5.3%")  # U+2212 ≠ ASCII hyphen


class TestPreservedInOutput(unittest.TestCase):
    def _thread_with(self, text):
        return {
            "source_url": "https://x.com/q/status/1", "tweet_id": "1",
            "author_name": "Q", "handle": "q", "posted_at": None, "lang": "en",
            "text": text, "media": [], "provider": "manual", "captured_at": "2026-06-26T00:00:00Z",
            "provenance": {"thread_completeness": "1 of 1", "capture_scope": "x"},
            "thread_items": [{"index": 1, "text": text, "url": "https://x.com/q/status/1",
                              "posted_at": None, "posted_at_utc": None, "media": []}],
        }

    def test_all_fixtures_survive_into_epub_chapter(self):
        text = "\n\n".join(FIXTURES) + "\n\n" + TABLE
        chapter = build_epub._thread_chapter(self._thread_with(text), "t", {})
        restored = html.unescape(chapter)
        for s in FIXTURES:
            self.assertIn(s, restored, f"missing from epub: {s!r}")
        for line in TABLE.split("\n"):
            self.assertIn(line, restored, f"table row lost in epub: {line!r}")

    def test_all_fixtures_survive_into_md(self):
        text = "\n\n".join(FIXTURES) + "\n\n" + TABLE
        md = build_md.render(self._thread_with(text), {})
        restored = html.unescape(md)
        for s in FIXTURES:
            self.assertIn(s, restored, f"missing from md: {s!r}")
        for line in TABLE.split("\n"):
            self.assertIn(line, restored, f"table row lost in md: {line!r}")

    def test_length_preservation(self):
        # Final visible text >= 0.95x source (plan §6.4). Entity-decode first so
        # the inflation from &amp; etc. doesn't mask real loss.
        text = "\n\n".join(FIXTURES)
        md = build_md.render(self._thread_with(text), {})
        visible = html.unescape(md)
        self.assertGreaterEqual(len(visible), 0.95 * len(text))


if __name__ == "__main__":
    unittest.main()
