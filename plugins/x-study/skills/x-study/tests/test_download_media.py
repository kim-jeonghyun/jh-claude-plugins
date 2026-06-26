import os, sys, tempfile, unittest
from unittest import mock
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import download_media  # noqa: E402

class TestDownload(unittest.TestCase):
    def test_host_allowlist(self):
        self.assertTrue(download_media.is_allowed_host("https://pbs.twimg.com/media/A.jpg?name=orig"))
        self.assertFalse(download_media.is_allowed_host("https://evil.example.com/a.jpg"))

    def test_host_allowlist_requires_https(self):
        self.assertFalse(download_media.is_allowed_host("http://pbs.twimg.com/a.jpg"))
        self.assertTrue(download_media.is_allowed_host("https://pbs.twimg.com/a.jpg"))

    def test_fetch_bytes_rejects_bad_host_without_network(self):
        with self.assertRaises(ValueError):
            download_media._fetch_bytes("https://evil.example.com/a.jpg")

    def test_ext_from_magic_bytes(self):
        self.assertEqual(download_media._ext_for(b"\xff\xd8\xff\xe0JFIF"), ".jpg")
        self.assertEqual(download_media._ext_for(b"\x89PNG\r\n\x1a\n...."), ".png")
        self.assertEqual(download_media._ext_for(b"GIF89a...."), ".gif")
        self.assertEqual(download_media._ext_for(b"RIFF\x00\x00\x00\x00WEBPVP8 "), ".webp")
        self.assertEqual(download_media._ext_for(b"unknownbytes"), ".jpg")  # safe default

    def test_png_download_named_png(self):
        canon = {"media": [{"type": "photo", "url": "https://pbs.twimg.com/media/A.png", "local_path": None}]}
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(download_media, "_fetch_bytes", lambda u, **k: b"\x89PNG\r\n\x1a\n\x00data"):
                out = download_media.download_all(canon, d)
            self.assertEqual(out["media"][0]["local_path"], "images/img1.png")  # extension from bytes
            self.assertTrue(os.path.exists(os.path.join(d, "images", "img1.png")))

    def test_download_photos_only_and_local_path(self):
        canon = {"media": [
            {"type": "photo", "url": "https://pbs.twimg.com/media/A.jpg?name=orig", "local_path": None},
            {"type": "video_thumb", "url": "https://pbs.twimg.com/media/V.jpg?name=orig", "local_path": None},
            {"type": "photo", "url": "https://evil.example.com/x.jpg", "local_path": None},
        ]}
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(download_media, "_fetch_bytes", lambda u, **k: b"\xff\xd8\xff\xe0JPEG"):
                out = download_media.download_all(canon, d)
            self.assertEqual(out["media"][0]["local_path"], "images/img1.jpg")   # photo, allowed
            self.assertIsNone(out["media"][1]["local_path"])                       # video_thumb skipped
            self.assertIsNone(out["media"][2]["local_path"])                       # disallowed host skipped
            self.assertTrue(os.path.exists(os.path.join(d, "images", "img1.jpg")))


class TestThreadTraversal(unittest.TestCase):
    def test_global_counter_across_thread_items(self):
        # thread_items is authoritative: top-level media must be IGNORED, and a
        # single global counter spans every tweet's photos.
        canon = {
            "media": [{"type": "photo", "url": "https://pbs.twimg.com/media/TOP.jpg", "local_path": None}],
            "thread_items": [
                {"index": 1, "media": [{"type": "photo", "url": "https://pbs.twimg.com/media/A.jpg", "local_path": None}]},
                {"index": 2, "media": [{"type": "photo", "url": "https://pbs.twimg.com/media/B.jpg", "local_path": None}]},
            ],
        }
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(download_media, "_fetch_bytes", lambda u, **k: b"\xff\xd8\xff\xe0JPEG"):
                out = download_media.download_all(canon, d)
            self.assertEqual(out["thread_items"][0]["media"][0]["local_path"], "images/img1.jpg")
            self.assertEqual(out["thread_items"][1]["media"][0]["local_path"], "images/img2.jpg")
            self.assertIsNone(out["media"][0]["local_path"])  # top-level ignored for threads
            self.assertTrue(os.path.exists(os.path.join(d, "images", "img1.jpg")))
            self.assertTrue(os.path.exists(os.path.join(d, "images", "img2.jpg")))
            self.assertFalse(os.path.exists(os.path.join(d, "images", "img3.jpg")))

    def test_per_item_ssrf_guard_off_allowlist_not_fetched(self):
        # An off-allowlist media URL in tweet 2 must NOT be fetched, must keep
        # local_path=null (rendered as a link), and must not consume a counter.
        fetched = []
        def spy_fetch(u, **k):
            fetched.append(u)
            return b"\xff\xd8\xff\xe0JPEG"
        canon = {
            "media": [], "thread_items": [
                {"index": 1, "media": [{"type": "photo", "url": "https://pbs.twimg.com/media/A.jpg", "local_path": None}]},
                {"index": 2, "media": [{"type": "photo", "url": "https://evil.example.com/x.jpg", "local_path": None}]},
                {"index": 3, "media": [{"type": "photo", "url": "https://pbs.twimg.com/media/C.jpg", "local_path": None}]},
            ],
        }
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(download_media, "_fetch_bytes", spy_fetch):
                out = download_media.download_all(canon, d)
        self.assertEqual(out["thread_items"][0]["media"][0]["local_path"], "images/img1.jpg")
        self.assertIsNone(out["thread_items"][1]["media"][0]["local_path"])      # off-allowlist kept as link
        self.assertEqual(out["thread_items"][2]["media"][0]["local_path"], "images/img2.jpg")  # counter not consumed by evil
        self.assertNotIn("https://evil.example.com/x.jpg", fetched)             # never fetched


if __name__ == "__main__":
    unittest.main()
