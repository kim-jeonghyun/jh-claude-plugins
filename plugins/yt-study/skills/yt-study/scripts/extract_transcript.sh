#!/bin/bash
# YouTube subtitle extraction (SRT format)
# Usage: ./extract_transcript.sh <URL> [output_dir]
#
# Tries subtitles in priority order, preferring manual over auto-generated and
# Korean over English. IMPORTANT: yt-dlp exits 0 even when a requested language
# is missing (it just prints "There are no subtitles for the requested
# languages"), so success is detected by checking for an actual output file --
# never by the exit code.

URL="$1"
OUTPUT_DIR="${2:-/tmp}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <YouTube URL> [output_dir]"
  exit 1
fi

# Validate URL is a YouTube domain
case "$URL" in
  https://www.youtube.com/*|https://youtube.com/*|https://youtu.be/*|https://m.youtube.com/*) ;;
  *) echo "ERROR: Only YouTube URLs are supported."; exit 1 ;;
esac

# Check yt-dlp is installed
if ! command -v yt-dlp &>/dev/null; then
  echo "ERROR: yt-dlp is not installed. Install with: brew install yt-dlp (macOS) / pip install yt-dlp (Linux/Windows)"
  exit 1
fi

OUT_BASE="$OUTPUT_DIR/yt_transcript"

# Capture yt-dlp's stderr so a real error (network / rate-limit / format) can be
# surfaced on failure instead of being silently mistaken for "no subtitles".
ERR_LOG="$(mktemp)"
trap 'rm -f "$ERR_LOG"' EXIT

# First existing file matching a glob (empty if none). Glob-based rather than
# `ls`, so it is safe with spaces in the output path and shellcheck-clean.
_first() { local f; for f in "$@"; do [ -e "$f" ] && { printf '%s' "$f"; return; }; done; }

# Priority order. "ko-orig" is YouTube's "Korean (Original)" track on
# natively-Korean videos and is the most faithful transcription, so it is tried
# before the (sometimes machine-translated) "ko" track.
#   manual ko-orig > manual ko > manual en > auto ko-orig > auto ko > auto en
# --convert-subs srt turns YouTube's native VTT into SRT (uses ffmpeg).
ATTEMPTS=(
  "--write-subs|ko-orig"
  "--write-subs|ko"
  "--write-subs|en"
  "--write-auto-subs|ko-orig"
  "--write-auto-subs|ko"
  "--write-auto-subs|en"
)

for attempt in "${ATTEMPTS[@]}"; do
  mode="${attempt%%|*}"
  lang="${attempt##*|}"
  if [ "$mode" = "--write-subs" ]; then kind="manual"; else kind="auto-generated"; fi

  # Clear between attempts so any file found belongs to THIS attempt/language.
  # This also preserves priority when ffmpeg is absent and only un-converted VTT
  # is produced: the first (highest-priority) attempt that yields anything wins.
  rm -f "$OUT_BASE".*.srt "$OUT_BASE".*.vtt 2>/dev/null
  yt-dlp "$mode" --sub-langs "$lang" --convert-subs srt --skip-download \
    -o "$OUT_BASE.%(ext)s" "$URL" >/dev/null 2>"$ERR_LOG"

  srt_file=$(_first "$OUT_BASE".*.srt)
  if [ -n "$srt_file" ]; then
    echo "Extracted $kind subtitles ($lang): $srt_file"
    exit 0
  fi

  # Track existed but SRT conversion failed (e.g. ffmpeg missing): keep the VTT
  # for this language rather than losing it.
  vtt_file=$(_first "$OUT_BASE".*.vtt)
  if [ -n "$vtt_file" ]; then
    echo "WARNING: Found $kind subtitles ($lang) but could not convert to SRT (is ffmpeg installed?). VTT: $vtt_file"
    exit 0
  fi
done

echo "ERROR: No ko/en subtitles (manual or auto-generated) found for this video." >&2
# Surface yt-dlp's last message (otherwise hidden) so real errors aren't masked.
[ -s "$ERR_LOG" ] && { echo "--- yt-dlp last message ---" >&2; cat "$ERR_LOG" >&2; }
exit 1
