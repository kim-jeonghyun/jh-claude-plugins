# Blog Digest

Blog article analysis with summary, insights, Korean translation, and comprehension quizzes.

## Installation

```bash
# 1. Add marketplace (if not already added)
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins

# 2. Install plugin
claude plugin install blog-digest@jh-claude-plugins
```

## Usage

```
블로그 정리해줘 https://example.com/article
```

Also: "blog digest", "블로그 요약", or any blog URL.

## First Run

On first use, the plugin asks you to configure:
1. **Save path** — where to save digest files
   - `blog-digests/` in current project (default)
   - Custom absolute path
   - Obsidian vault (see [Obsidian Integration](#obsidian-integration-optional) below)
   - Notion (see [Notion Integration](#notion-integration-optional) below)
2. **Categories** — folder categories for organizing digests (e.g., `tech, business, investing`)
3. **Scope** — apply settings globally (all projects) or to the current project only

Settings are stored in MEMORY.md (project-level or global `~/.claude/memory/MEMORY.md`).

## Features

- **No dependencies** — WebFetch-based content extraction, no external tools needed
- **Structured summary** with key points and insights
- **Full Korean translation** for English articles
- **3-level comprehension quiz** (9 questions)
- **Deep Research** follow-up option
- **Output flexibility**: Obsidian / Notion / local file save
- **Configurable** save path and categories

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
    2026-03-08-article-title.md
  investing/
    2026-03-07-another-article.md
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
2. Content extraction (WebFetch)
3. Context gathering (WebSearch)
4. Document generation (summary + insights + full text)
5. Category & file save
6. Study quiz (3 levels x 3 questions)
7. Follow-up (re-quiz / deep research / done)
