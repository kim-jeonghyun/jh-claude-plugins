import os, sys, tempfile, unittest
from unittest import mock
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import download_media  # noqa: E402

class TestDownload(unittest.TestCase):
    def test_host_allowlist(self):
        self.assertTrue(download_media.is_allowed_host("https://pbs.twimg.com/media/A.jpg?name=orig"))
        self.assertFalse(download_media.is_allowed_host("https://evil.example.com/a.jpg"))

    def test_fetch_bytes_rejects_bad_host_without_network(self):
        with self.assertRaises(ValueError):
            download_media._fetch_bytes("https://evil.example.com/a.jpg")

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

if __name__ == "__main__":
    unittest.main()
