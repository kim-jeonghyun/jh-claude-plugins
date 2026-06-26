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


def thread_canon():
    return {
        "source_url": "https://x.com/q/status/100", "tweet_id": "100",
        "author_name": "Quant", "handle": "q",
        "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "lang": "en",
        "text": "Tweet one $AAPL +12.5%.", "media": [],  # top-level ignored for threads
        "provider": "manual", "captured_at": "2026-06-26T00:00:00Z",
        "provenance": {
            "source_url": "https://x.com/q/status/100",
            "captured_at": "2026-06-26T00:00:00Z",
            "capture_method": "manual paste, x-study v0.2",
            "thread_completeness": "2 of 2",
            "capture_scope": "Excludes: quoted tweets, video/GIF media.",
        },
        "thread_items": [
            {"index": 1, "text": "Tweet one $AAPL +12.5%.", "url": "https://x.com/q/status/100",
             "posted_at": "Wed Jun 24 11:52:51 +0000 2026", "posted_at_utc": "2026-06-24T11:52:51Z",
             "media": [{"type": "photo", "url": "x", "local_path": "images/img1.jpg"}]},
            {"index": 2, "text": "Tweet two <script>alert(1)</script>\n\nRow1   100\nRow2   200",
             "url": "https://x.com/q/status/101", "posted_at": None, "posted_at_utc": None,
             "media": [{"type": "photo", "url": "y", "local_path": "images/img2.jpg"}]},
        ],
    }

def _write_two_imgs(d):
    os.makedirs(os.path.join(d, "images"), exist_ok=True)
    for n in (1, 2):
        with open(os.path.join(d, "images", f"img{n}.jpg"), "wb") as f:
            f.write(b"\xff\xd8\xff\xe0JPEG" + bytes([n]))

class TestThreadRender(unittest.TestCase):
    def test_per_tweet_sections_banner_and_images(self):
        canon = thread_canon()
        enrich = {"title": "Quant - Thread",
                  "alt_texts": {"images/img1.jpg": "Chart A", "images/img2.jpg": "Chart B"}}
        with tempfile.TemporaryDirectory() as d:
            _write_two_imgs(d)
            out = os.path.join(d, "out.epub")
            build_epub.build(canon, out, img_dir=d, enrichment=enrich)
            with zipfile.ZipFile(out) as z:
                ch = z.read("OEBPS/chapter1.xhtml").decode("utf-8")
                # per-tweet archive labels (NOT author n/n) + permalinks
                self.assertIn("Captured tweet 1 of 2", ch)
                self.assertIn("Captured tweet 2 of 2", ch)
                self.assertIn("https://x.com/q/status/101", ch)        # per-tweet permalink
                # completeness banner present
                self.assertIn("2 of 2", ch)
                self.assertIn('role="note"', ch)
                # both charts embedded under their own tweet, with alts
                self.assertIn("images/img1.jpg", ch)
                self.assertIn("images/img2.jpg", ch)
                self.assertIn("Chart A", ch); self.assertIn("Chart B", ch)
                # security: script in a tweet is escaped, never live
                self.assertIn("&lt;script&gt;", ch)
                self.assertNotIn("<script>alert", ch)
                # financial content preserved
                self.assertIn("$AAPL +12.5%", ch)
                # tabular block -> <pre> (alignment preserved)
                self.assertIn("<pre", ch)
                self.assertIn("Row1   100", ch)
                # OPF: two distinct image ids, no collision
                opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn('id="img1"', opf); self.assertIn('id="img2"', opf)
                self.assertEqual(z.namelist()[0], "mimetype")
                self.assertIn("OEBPS/images/img1.jpg", z.namelist())
                self.assertIn("OEBPS/images/img2.jpg", z.namelist())

    def test_thread_epub_byte_deterministic(self):
        canon = thread_canon()
        enrich = {"title": "Quant - Thread", "alt_texts": {}}
        with tempfile.TemporaryDirectory() as d:
            _write_two_imgs(d)
            a = os.path.join(d, "a.epub"); b = os.path.join(d, "b.epub")
            build_epub.build(canon, a, img_dir=d, enrichment=enrich)
            build_epub.build(canon, b, img_dir=d, enrichment=enrich)
            import filecmp
            self.assertTrue(filecmp.cmp(a, b, shallow=False), "EPUB not byte-deterministic")
            # prove determinism by construction (fixed epoch), not by timing luck
            with zipfile.ZipFile(a) as z:
                self.assertEqual(z.getinfo("OEBPS/content.opf").date_time, (1980, 1, 1, 12, 1, 0))

    def test_single_tweet_byte_deterministic(self):
        canon = base_canon()
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "images"))
            with open(os.path.join(d, "images", "img1.jpg"), "wb") as f:
                f.write(b"\xff\xd8\xff\xe0JPEG")
            a = os.path.join(d, "a.epub"); b = os.path.join(d, "b.epub")
            build_epub.build(canon, a, img_dir=d, enrichment=None)
            build_epub.build(canon, b, img_dir=d, enrichment=None)
            import filecmp
            self.assertTrue(filecmp.cmp(a, b, shallow=False), "single-tweet EPUB not deterministic")

if __name__ == "__main__":
    unittest.main()
