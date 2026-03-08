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
1. **Save path** — where to save digest files
   - `video-digests/` in current project (default)
   - Custom absolute path
   - Obsidian vault (see [Obsidian Integration](#obsidian-integration-optional) below)
   - Notion (see [Notion Integration](#notion-integration-optional) below)
2. **Categories** — folder categories for organizing digests (e.g., `tech, business, investing`)
3. **Scope** — apply settings globally (all projects) or to the current project only

Settings are stored in MEMORY.md (project-level or global `~/.claude/memory/MEMORY.md`).

## Features

- **Adaptive depth**: SHORT (<30min) / MEDIUM (30min-2h) / LONG (2h+)
- **Topic segmentation**: 2-pass analysis for 30min+ videos (auto-detected topics with timestamps)
- **Quiz scaling**: 9-15 questions based on video length
- **Bug fix**: SRT subtitle format (upstream json3 was broken)
- **Output flexibility**: Obsidian / Notion / local file save
- **Subtitle priority**: manual subtitles preferred over auto-generated
- **Cross-platform**: macOS, Linux, Windows supported

## Obsidian Integration (Optional)

To save digests directly into your Obsidian vault:

1. During first run, choose **"Obsidian vault"** as save path
2. Enter the absolute path to your vault folder:
   ```
   # macOS example
   /Users/yourname/Documents/ObsidianVault

   # Linux example
   /home/yourname/ObsidianVault

   # Windows example
   C:\Users\yourname\Documents\ObsidianVault
   ```
3. Set up your categories (these become subfolders in the vault)

Digests are saved as standard Markdown with YAML frontmatter, fully compatible with Obsidian:

```
YourVault/
  tech/
    2026-03-08-video-title.md
  investing/
    2026-03-07-another-video.md
```

## Notion Integration (Optional)

For direct Notion save (instead of copy-paste), set up the official Notion MCP server:

1. Create a Notion Integration at https://www.notion.so/profile/integrations
   - Enable: Read content, Insert content, Update content
   - Copy the generated token (`ntn_...` or `secret_...`)

2. Connect your Notion pages: Open target page → `···` → Connections → Add your integration

3. Install the MCP server:
   ```bash
   claude mcp add notion -- npx -y @notionhq/notion-mcp-server
   # When prompted, enter your NOTION_TOKEN
   ```

4. During first run, choose "Notion (copy-paste)" as save target. The plugin auto-detects the MCP server and saves directly.

Without the MCP server, the plugin still works — it generates the document and prompts you to copy-paste into Notion.

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
