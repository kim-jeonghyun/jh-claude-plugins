import os, sys, tempfile, unittest, zipfile
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_epub  # noqa: E402

def base_canon():
    return {
        "source_url": "https://x.com/markminervini/status/2069750598728089949",
        "tweet_id": "2069750598728089949",
        "author_name": "Mark Minervini", "handle": "markminervini",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "First paragraph with <b> & ampersand.\nSecond paragraph.",
        "media": [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}],
        "provider": "fxtwitter", "captured_at": "2026-06-25T00:00:00Z", "tags": ["macro"],
    }

class TestHelpers(unittest.TestCase):
    def test_split_single_and_double_newlines(self):
        self.assertEqual(build_epub.split_paragraphs("a\nb"), ["a", "b"])
        self.assertEqual(build_epub.split_paragraphs("a\n\n\nb"), ["a", "b"])
    def test_escape(self):
        self.assertEqual(build_epub.esc("a<b>&\"'"), "a&lt;b&gt;&amp;&quot;&#39;")
    def test_default_title(self):
        self.assertIn("Mark Minervini", build_epub.default_title(base_canon()))
    def test_slugify(self):
        self.assertEqual(build_epub.slugify("Mark Minervini - Market Analysis!"), "mark-minervini-market-analysis")

class TestBuild(unittest.TestCase):
    def test_epub_structure_and_enrichment(self):
        canon = base_canon()
        enrich = {"title": "Mark Minervini - Market Analysis",
                  "alt_texts": {"images/img1.jpg": "Bull Markets S&P 500 Chart"}}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "images"))
            with open(os.path.join(d, "images", "img1.jpg"), "wb") as f:
                f.write(b"\xff\xd8\xff\xe0JPEG")
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=enrich)
            self.assertTrue(zipfile.is_zipfile(out))
            with zipfile.ZipFile(out) as z:
                names = z.namelist()
                self.assertEqual(names[0], "mimetype")
                self.assertEqual(z.getinfo("mimetype").compress_type, zipfile.ZIP_STORED)
                self.assertEqual(z.read("mimetype"), b"application/epub+zip")
                self.assertIn("OEBPS/images/img1.jpg", names)
                ch = z.read("OEBPS/chapter1.xhtml").decode("utf-8")
                self.assertIn("&lt;b&gt;", ch)                       # escaped body
                self.assertIn("Second paragraph.", ch)               # both paragraphs
                self.assertIn("Bull Markets S&amp;P 500 Chart", ch)  # enrichment alt (escaped)
                self.assertNotIn("�", ch)                       # no mojibake
                css = z.read("OEBPS/style.css").decode("utf-8")
                self.assertIn("Apple Color Emoji", css)              # emoji fallback
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("Mark Minervini - Market Analysis", opf)  # enrichment title

    def test_default_title_when_no_enrichment(self):
        canon = base_canon(); canon["media"] = []
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=None)
            with zipfile.ZipFile(out) as z:
                self.assertIn("Mark Minervini", z.read("OEBPS/content.opf").decode("utf-8"))

    def test_fallback_link_for_non_embedded_media(self):
        canon = base_canon()
        canon["media"] = [
            {"type": "video", "url": "https://video.twimg.com/v.mp4", "local_path": None},
        ]
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=None)
            with zipfile.ZipFile(out) as z:
                ch = z.read("OEBPS/chapter1.xhtml").decode("utf-8")
                self.assertIn('<a href="https://video.twimg.com/v.mp4"', ch)
                self.assertIn("media not embedded", ch)

    def test_dcterms_modified_from_posted_at(self):
        canon = base_canon()  # posted_at = "Wed Jun 24 11:52:51 +0000 2026"
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=None)
            with zipfile.ZipFile(out) as z:
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("2026-06-24", opf)
                self.assertIn('property="dcterms:modified">2026-06-24T11:52:51Z', opf)

    def test_dcterms_modified_fallback_when_unparseable(self):
        canon = base_canon(); canon["posted_at"] = None
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=None)
            with zipfile.ZipFile(out) as z:
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("2026-01-01T00:00:00Z", opf)

if __name__ == "__main__":
    unittest.main()
