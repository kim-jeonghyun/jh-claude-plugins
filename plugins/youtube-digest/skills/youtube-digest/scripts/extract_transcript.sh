#!/bin/bash
# YouTube subtitle extraction (SRT format)
# Usage: ./extract_transcript.sh <URL> [output_dir]

URL="$1"
OUTPUT_DIR="${2:-/tmp}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <YouTube URL> [output_dir]"
  exit 1
fi

# Validate URL format
case "$URL" in
  https://*|http://*) ;;
  *) echo "ERROR: Invalid URL. Must start with http:// or https://"; exit 1 ;;
esac

# Check yt-dlp is installed
if ! command -v yt-dlp &>/dev/null; then
  echo "ERROR: yt-dlp is not installed. Install with: brew install yt-dlp (macOS) / pip install yt-dlp (Linux/Windows)"
  exit 1
fi

# SRT format (stable). Original used --convert-subs json3 which is invalid.
if ! yt-dlp --write-auto-sub --sub-lang "ko,en" --sub-format srt --skip-download \
  -o "$OUTPUT_DIR/yt_transcript.%(ext)s" "$URL"; then
  echo "ERROR: Failed to extract subtitles. The video may not have subtitles available."
  exit 1
fi
