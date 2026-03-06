#!/bin/bash
# YouTube metadata extraction
# Usage: ./extract_metadata.sh <URL>

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: $0 <YouTube URL>"
  exit 1
fi

# Reject playlist URLs — only single video supported
case "$URL" in
  *list=*|*playlist*)
    echo "ERROR: Playlist URLs are not supported. Please provide a single video URL."
    exit 1
    ;;
esac

yt-dlp --dump-json --no-download "$URL" 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"title: {data.get('title', 'N/A')}\")
print(f\"channel: {data.get('channel', data.get('uploader', 'N/A'))}\")
print(f\"upload_date: {data.get('upload_date', 'N/A')}\")
print(f\"duration: {data.get('duration_string', 'N/A')}\")
print(f\"duration_seconds: {data.get('duration', 0)}\")
print(f\"description: {data.get('description', 'N/A')[:200]}\")
print(f\"tags: {', '.join(data.get('tags', [])[:10])}\")
print(f\"is_live: {data.get('is_live', False)}\")
"
