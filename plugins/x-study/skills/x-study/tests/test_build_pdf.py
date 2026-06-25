import os, sys, unittest
from unittest import mock
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import build_pdf  # noqa: E402

class TestPdf(unittest.TestCase):
    def test_pandoc_args_safe(self):
        args = build_pdf.pandoc_args("in.md", "out.pdf", "weasyprint")
        self.assertIsInstance(args, list)
        self.assertEqual(args[0], "pandoc")
        self.assertIn("--pdf-engine=weasyprint", args)
        self.assertIn("--", args)
        self.assertTrue(args[-1].endswith("in.md"))
        self.assertTrue(os.path.isabs(args[-1]))           # absolute input path
        self.assertGreater(args.index("--"), args.index("-o"))

    def test_build_fails_gracefully_without_pandoc(self):
        with mock.patch.object(build_pdf, "_which", lambda x: None):
            ok, msg = build_pdf.build("in.md", "out.pdf")
        self.assertFalse(ok)
        self.assertIn("pandoc", msg.lower())

    def test_detect_engine_prefers_order(self):
        with mock.patch.object(build_pdf, "_which",
                               lambda x: "/bin/" + x if x in ("wkhtmltopdf", "typst") else None):
            self.assertEqual(build_pdf.detect_engine(), "wkhtmltopdf")

if __name__ == "__main__":
    unittest.main()
