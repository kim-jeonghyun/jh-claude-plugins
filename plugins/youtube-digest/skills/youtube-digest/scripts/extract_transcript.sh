#!/bin/bash
# YouTube subtitle extraction (SRT format)
# Usage: ./extract_transcript.sh <URL> [output_dir]

URL="$1"
OUTPUT_DIR="${2:-/tmp}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <YouTube URL> [output_dir]"
  exit 1
fi

# SRT format (stable). Original used --convert-subs json3 which is invalid.
yt-dlp --write-auto-sub --sub-lang "ko,en" --sub-format srt --skip-download \
  -o "$OUTPUT_DIR/yt_transcript.%(ext)s" "$URL"
