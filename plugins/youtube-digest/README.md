# YouTube Digest

YouTube video analysis with adaptive depth based on video length.

Based on [youtube-digest](https://github.com/team-attention/claude-plugins) by Team Attention (MIT License).

## What's Different (v1.0.0)

- **Adaptive templates**: SHORT (<30min) / MEDIUM (30min-2h) / LONG (2h+)
- **Topic segmentation**: 2-pass analysis for 30min+ videos
- **Quiz scaling**: 9-15 questions based on video length
- **Bug fix**: SRT subtitle format (json3 was broken)
- **Output flexibility**: Obsidian / Notion / local file save

## Prerequisites

yt-dlp is required for metadata and subtitle extraction:

```bash
# macOS
brew install yt-dlp

# Linux
pip install yt-dlp

# Windows
winget install yt-dlp
```

## Usage

```
유튜브 정리해줘 https://www.youtube.com/watch?v=xxxxx
```

Also: "영상 요약", "transcript 번역", "YouTube digest", "영상 퀴즈"
