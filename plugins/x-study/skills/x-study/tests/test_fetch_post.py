import os, sys, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import fetch_post  # noqa: E402

class TestParse(unittest.TestCase):
    def test_parse_x_url(self):
        self.assertEqual(fetch_post.parse_url("https://x.com/foo/status/123"), ("foo", "123"))
    def test_parse_twitter_url(self):
        self.assertEqual(fetch_post.parse_url("https://twitter.com/Bar_1/status/999?s=20"), ("Bar_1", "999"))
    def test_reject_non_status(self):
        with self.assertRaises(ValueError):
            fetch_post.parse_url("https://example.com/foo")

class TestNormalize(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "fixtures", "fxtwitter.json")) as f:
            self.raw = f.read()
    def test_fields_and_unescape(self):
        c = fetch_post.normalize_fxlike(self.raw, "markminervini", "2069750598728089949")
        self.assertEqual(c["author_name"], "Mark Minervini")
        self.assertEqual(c["handle"], "markminervini")
        self.assertIn("Risk & reward", c["text"])     # &amp; -> &
        self.assertNotIn("title", c)                    # title lives in enrichment.json
        self.assertEqual(len(c["media"]), 2)
        self.assertNotIn("alt", c["media"][0])          # alt lives in enrichment.json
        self.assertEqual(c["media"][0]["url"], "https://pbs.twimg.com/media/AAA.jpg?name=orig")
        self.assertEqual(c["thread_items"], [])
    def test_truncation_detection(self):
        self.assertTrue(fetch_post.looks_truncated("blah… Show more"))
        self.assertTrue(fetch_post.looks_truncated("ends with ellipsis…"))
        self.assertFalse(fetch_post.looks_truncated("complete sentence."))

if __name__ == "__main__":
    unittest.main()
