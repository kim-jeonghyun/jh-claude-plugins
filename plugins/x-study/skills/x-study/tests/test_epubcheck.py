"""Structural EPUB validity via W3C epubcheck (v5.3.0). Skips when epubcheck is
unavailable (local dev); CI installs it and sets EPUBCHECK_JAR. Catches
mimetype/OPF/spine errors that byte-equality goldens cannot.
"""
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_epub  # noqa: E402
from test_build_epub import thread_canon, _write_two_imgs  # noqa: E402


def _epubcheck_cmd():
    jar = os.environ.get("EPUBCHECK_JAR")
    if jar and os.path.exists(jar) and shutil.which("java"):
        return ["java", "-jar", jar]
    if shutil.which("epubcheck"):
        return ["epubcheck"]
    return None


class TestEpubcheck(unittest.TestCase):
    def test_thread_epub_is_valid(self):
        cmd = _epubcheck_cmd()
        if not cmd:
            self.skipTest("epubcheck/java not available (CI installs it)")
        enrich = {"title": "Quant - Thread",
                  "alt_texts": {"images/img1.jpg": "Chart A", "images/img2.jpg": "Chart B"}}
        with tempfile.TemporaryDirectory() as d:
            _write_two_imgs(d)
            out = os.path.join(d, "thread.epub")
            build_epub.build(thread_canon(), out, img_dir=d, enrichment=enrich)
            r = subprocess.run(cmd + [out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"epubcheck failed:\n{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main()
