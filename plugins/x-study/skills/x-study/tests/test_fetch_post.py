import json, os, sys, unittest
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
        # ellipsis CHARACTER and "Show more" trigger; bare three dots do not
        self.assertFalse(fetch_post.looks_truncated("normal prose ..."))
        self.assertTrue(fetch_post.looks_truncated("text…"))
        self.assertTrue(fetch_post.looks_truncated("x Show more"))

    def test_media_all_videos_and_gifs(self):
        raw = json.dumps({
            "code": 200, "message": "OK",
            "tweet": {
                "url": "https://x.com/foo/status/1", "id": "1",
                "text": "post", "lang": "en",
                "created_at": "Wed Jun 24 11:52:51 +0000 2026",
                "author": {"name": "Foo", "screen_name": "foo"},
                "media": {"all": [
                    {"type": "photo", "url": "https://pbs.twimg.com/media/P.jpg", "width": 100, "height": 50},
                    {"type": "video", "url": "https://video.twimg.com/v.mp4", "width": 640, "height": 360},
                ]},
            },
        })
        c = fetch_post.normalize_fxlike(raw, "foo", "1")
        self.assertEqual(len(c["media"]), 2)
        photo = c["media"][0]
        self.assertEqual(photo["type"], "photo")
        self.assertEqual(photo["url"], "https://pbs.twimg.com/media/P.jpg")
        video = c["media"][1]
        self.assertEqual(video["type"], "video")
        self.assertEqual(video["url"], "https://video.twimg.com/v.mp4")
        self.assertIsNone(video["local_path"])

    def test_media_photos_fallback_when_no_all(self):
        c = fetch_post.normalize_fxlike(self.raw, "markminervini", "2069750598728089949")
        self.assertEqual(len(c["media"]), 2)
        self.assertEqual(c["media"][0]["type"], "photo")  # fallback yields photos
        self.assertEqual(c["media"][0]["url"], "https://pbs.twimg.com/media/AAA.jpg?name=orig")

import tempfile  # noqa: E402
from unittest import mock  # noqa: E402

class TestChain(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "fixtures", "fxtwitter.json")) as f:
            self.good = f.read()

    def test_fallback_to_vxtwitter_on_error(self):
        calls = []
        def fake_get(u, timeout=20):
            calls.append(u)
            if "api.fxtwitter.com" in u:
                raise RuntimeError("boom")
            return self.good
        with mock.patch.object(fetch_post, "_http_get", fake_get):
            c = fetch_post.fetch("https://x.com/markminervini/status/2069750598728089949")
        self.assertEqual(c["provider"], "vxtwitter")
        self.assertEqual(len(calls), 2)

    def test_truncated_first_provider_tries_next(self):
        trunc = self.good.replace("Line two of the post.", "Line two of the… Show more")
        def fake_get(u, timeout=20):
            return trunc if "fxtwitter" in u else self.good
        with mock.patch.object(fetch_post, "_http_get", fake_get):
            c = fetch_post.fetch("https://x.com/markminervini/status/2069750598728089949")
        self.assertEqual(c["provider"], "vxtwitter")
        self.assertFalse(c["truncated"])

    def test_raw_sidecar_written(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(fetch_post, "_http_get", lambda u, timeout=20: self.good):
                c = fetch_post.fetch("https://x.com/markminervini/status/2069750598728089949", raw_dir=d)
            self.assertTrue(os.path.exists(os.path.join(d, c["raw_provider_ref"])))

    def test_all_fail_raises(self):
        with mock.patch.object(fetch_post, "_http_get", mock.Mock(side_effect=RuntimeError("x"))):
            with self.assertRaises(RuntimeError):
                fetch_post.fetch("https://x.com/a/status/1")

    def test_captured_at_set_on_fetch(self):
        with mock.patch.object(fetch_post, "_http_get", lambda u, timeout=20: self.good):
            c = fetch_post.fetch("https://x.com/markminervini/status/2069750598728089949")
        self.assertIsNotNone(c["captured_at"])
        self.assertIsInstance(c["captured_at"], str)
        self.assertTrue(c["captured_at"].endswith("Z"))

    def test_http_get_strict_decode_raises_on_invalid_bytes(self):
        class FakeResp:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"\xff\xfe"
        with mock.patch.object(fetch_post.urllib.request, "urlopen", lambda *a, **k: FakeResp()):
            with self.assertRaises(UnicodeDecodeError):
                fetch_post._http_get("https://api.fxtwitter.com/x/status/1")

if __name__ == "__main__":
    unittest.main()
