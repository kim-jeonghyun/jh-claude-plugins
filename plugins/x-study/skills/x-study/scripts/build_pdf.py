#!/usr/bin/env python3
"""Build a PDF from a markdown file via pandoc (optional, lossy).

Usage: python3 build_pdf.py <in.md> <out.pdf>
Exit 0 on success; exit 3 with install guidance if pandoc/engine is missing.
"""
import argparse, os, shutil, subprocess, sys

ENGINES = ["weasyprint", "wkhtmltopdf", "typst", "xelatex", "pdflatex", "tectonic"]

def _which(name):
    return shutil.which(name)

def detect_engine():
    for e in ENGINES:
        if _which(e):
            return e
    return None

def pandoc_args(md, out, engine):
    # `-f markdown-tex_math_dollars`: cashtags like "$AAPL ... $TSLA" must NOT be
    # parsed as LaTeX inline math (which would silently eat the text between them).
    # absolute paths + `--` so a file named like `--flag.md` cannot be parsed as an option.
    return ["pandoc", "-f", "markdown-tex_math_dollars", f"--pdf-engine={engine}",
            "-o", os.path.abspath(out), "--", os.path.abspath(md)]

def build(md_path, out_pdf):
    if not _which("pandoc"):
        return False, "pandoc not found. Install: brew install pandoc"
    engine = detect_engine()
    if not engine:
        return False, "No PDF engine found. Install one, e.g.: brew install weasyprint (or wkhtmltopdf / typst)"
    try:
        subprocess.run(pandoc_args(md_path, out_pdf, engine), check=True)
        return True, out_pdf
    except subprocess.CalledProcessError as e:
        return False, f"pandoc failed (engine={engine}): {e}"

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("in_md")
    ap.add_argument("out_pdf")
    args = ap.parse_args(argv)
    ok, msg = build(args.in_md, args.out_pdf)
    print(msg)
    return 0 if ok else 3

if __name__ == "__main__":
    sys.exit(main())
