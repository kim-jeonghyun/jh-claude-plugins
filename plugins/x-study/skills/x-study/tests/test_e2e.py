import os, sys, tempfile, unittest, zipfile
from unittest import mock
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import fetch_post, download_media, build_epub  # noqa: E402

class TestE2E(unittest.TestCase):
    def test_fetch_to_epub(self):
        with open(os.path.join(HERE, "fixtures", "fxtwitter.json")) as f:
            raw = f.read()
        canon = fetch_post.normalize_fxlike(raw, "markminervini", "2069750598728089949")
        canon["provider"] = "fxtwitter"
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(download_media, "_fetch_bytes", lambda u, **k: b"\xff\xd8\xff\xe0JPEG"):
                canon = download_media.download_all(canon, d)
            enrich = {"title": "Mark Minervini - Market Analysis",
                      "alt_texts": {m["local_path"]: "Chart" for m in canon["media"] if m["local_path"]}}
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=enrich)
            self.assertTrue(zipfile.is_zipfile(out))
            with zipfile.ZipFile(out) as z:
                self.assertEqual(z.namelist()[0], "mimetype")
                self.assertIn("OEBPS/images/img1.jpg", z.namelist())
                self.assertIn("OEBPS/images/img2.jpg", z.namelist())
                self.assertIn("Mark Minervini - Market Analysis",
                              z.read("OEBPS/content.opf").decode("utf-8"))

if __name__ == "__main__":
    unittest.main()
