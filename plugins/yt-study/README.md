# YT Study

YouTube video study notes with adaptive depth based on video length.

## Attribution

This plugin is a fork of **youtube-digest** by [Team Attention](https://github.com/team-attention) (MIT License).

The original plugin provided YouTube video summarization for Claude Code. This fork was built on that foundation and adds 7 concrete improvements:

1. **Adaptive depth analysis** — SHORT / MEDIUM / LONG presets based on video duration
2. **2-pass topic segmentation** — auto-detected topic boundaries with timestamps for 30min+ videos
3. **Comprehension quizzes** — 3-level study quizzes scaled by video length (9-15 questions)
4. **SRT subtitle extraction** — more reliable format (avoids upstream json3 parsing issues)
5. **Obsidian / Notion integration** — direct save to note-taking platforms
6. **Multi-language support** — configurable output language (Korean, English, Japanese, etc.)
7. **Deep Research follow-up** — optional web deep-dive after quiz

See [LICENSE.original](LICENSE.original) for the original MIT license text.

> **Note**: The original repository (`team-attention/claude-plugins`) is no longer publicly available (confirmed on 2026-03-09).

## Installation

```bash
# 1. Add marketplace (if not already added)
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins

# 2. Install plugin
claude plugin install yt-study@jh-claude-plugins
```

### Migrating from youtube-digest

If you previously used the legacy `youtube-digest` plugin name (from team-attention or this repo):

1. Uninstall the legacy plugin: `claude plugin uninstall youtube-digest`
2. Install the new plugin: `claude plugin install yt-study@jh-claude-plugins`
3. Update your MEMORY.md config heading: `## YouTube Digest Settings` -> `## YT Study Settings`
4. Verify migration: run `claude plugin list` and confirm only `yt-study@jh-claude-plugins` is active.

## Prerequisites

yt-dlp and python3 are required for metadata and subtitle extraction:

```bash
# macOS
brew install yt-dlp python3

# Linux
sudo apt install python3 && pip install yt-dlp

# Windows (WSL recommended)
# 1. Install WSL: wsl --install
# 2. Inside WSL terminal:
sudo apt install python3 && pip install yt-dlp
```

> **Windows users**: This plugin uses shell scripts (`.sh`). You need [WSL](https://learn.microsoft.com/windows/wsl/install) or [Git Bash](https://gitforwindows.org/) to run them. Install yt-dlp and python3 **inside your WSL/Git Bash environment**, not via winget.

## Usage

```
유튜브 정리해줘 https://www.youtube.com/watch?v=xxxxx
```

Also: "영상 요약", "transcript 번역", "YouTube study", "영상 퀴즈"

## First Run

On first use, the plugin asks you to configure:
1. **Save path** — where to save study notes
   - `video-notes/` in current project (default)
   - Custom absolute path
   - Obsidian vault (see [Obsidian Integration](#obsidian-integration-optional) below)
   - Notion (see [Notion Integration](#notion-integration-optional) below)
2. **Categories** — folder categories for organizing notes (e.g., `tech, business, investing`)
3. **Language** — output language (Korean, English, Japanese, or custom)
4. **Scope** — apply settings globally (all projects) or to the current project only

Settings are stored in MEMORY.md (project-level or global `~/.claude/memory/MEMORY.md`).

## Features

- **Adaptive depth**: SHORT (<30min) / MEDIUM (30min-2h) / LONG (2h+)
- **Topic segmentation**: 2-pass analysis for 30min+ videos (auto-detected topics with timestamps)
- **Quiz scaling**: 9-15 questions based on video length
- **SRT subtitle extraction**: reliable format (avoids upstream json3 issues)
- **Output flexibility**: Obsidian / Notion / local file save
- **Subtitle priority**: manual subtitles preferred over auto-generated
- **Cross-platform**: macOS, Linux, Windows supported

## Obsidian Integration (Optional)

To save study notes directly into your Obsidian vault:

1. During first run, choose **"Obsidian vault"** as save path
2. Enter the absolute path to your vault folder:
   ```
   # macOS (local)
   /Users/yourname/Documents/ObsidianVault

   # macOS (iCloud sync)
   /Users/yourname/Library/Mobile Documents/iCloud~md~obsidian/Documents/VaultName

   # macOS (Google Drive)
   /Users/yourname/Library/CloudStorage/GoogleDrive-you@gmail.com/My Drive/ObsidianVault

   # macOS (Dropbox)
   /Users/yourname/Dropbox/ObsidianVault

   # Linux (local)
   /home/yourname/ObsidianVault

   # Windows (local)
   C:\Users\yourname\Documents\ObsidianVault

   # Windows (OneDrive)
   C:\Users\yourname\OneDrive\ObsidianVault
   ```

   > **Tip**: Not sure where your vault is? Open Obsidian → Settings → Files and links → check "Vault path" at the top.
3. Set up your categories (these become subfolders in the vault)

Study notes are saved as standard Markdown with YAML frontmatter, fully compatible with Obsidian:

```
YourVault/
  tech/
    2026-03-08-video-title.md
  investing/
    2026-03-07-another-video.md
```

## Notion Integration (Optional)

Two options for saving to Notion:

**Option A: Direct save via MCP (recommended)**

1. Create a Notion Integration at https://www.notion.so/profile/integrations
   - Enable: Read content, Insert content, Update content
   - Copy the generated token (`ntn_...` or `secret_...`)

2. Connect your Notion pages: Open target page → `···` → Connections → Add your integration

3. Install the MCP server:
   ```bash
   claude mcp add notion -- npx -y @notionhq/notion-mcp-server
   # When prompted, enter your NOTION_TOKEN
   ```

4. During first run, choose **"Notion"** as save target. The plugin auto-detects the MCP server and saves directly.

**Option B: Copy-paste (no setup needed)**

If you skip MCP setup, the plugin generates the document and displays it for you to copy-paste into Notion manually.

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
