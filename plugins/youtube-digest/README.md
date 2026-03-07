# YouTube Digest

YouTube video analysis with adaptive depth based on video length.

Based on [youtube-digest](https://github.com/team-attention/claude-plugins) by Team Attention (MIT License).

## Installation

```bash
# 1. Add marketplace (if not already added)
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins

# 2. Install plugin
claude plugin install youtube-digest@jh-claude-plugins
```

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

## First Run

On first use, the plugin asks you to configure:
1. **Save path** - where to save digest files (default: `video-digests/` in current project, or Obsidian vault)
2. **Categories** - folder categories for organizing digests

Settings are stored in your project's MEMORY.md.

## Features

- **Adaptive depth**: SHORT (<30min) / MEDIUM (30min-2h) / LONG (2h+)
- **Topic segmentation**: 2-pass analysis for 30min+ videos (auto-detected topics with timestamps)
- **Quiz scaling**: 9-15 questions based on video length
- **Bug fix**: SRT subtitle format (upstream json3 was broken)
- **Output flexibility**: Obsidian / Notion / local file save
- **Subtitle priority**: manual subtitles preferred over auto-generated
- **Cross-platform**: macOS, Linux, Windows supported

## Workflow

1. Config check (first run: setup wizard)
2. Metadata extraction (yt-dlp)
3. Processing strategy (preset selection based on duration)
4. Transcript extraction (SRT subtitles, ko/en)
5. Topic segmentation (MEDIUM/LONG: 2-pass analysis)
6. Context gathering (WebSearch)
7. Transcript correction (proper nouns, technical terms)
8. Document generation (adaptive template)
9. Category & file save
10. Study quiz (3 levels, scaled by preset)
11. Follow-up (re-quiz / deep research / done)
