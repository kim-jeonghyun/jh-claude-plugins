# Article Study

Blog and web article study notes with summaries, insights, translation, and comprehension quizzes.

## Installation

```bash
# 1. Add marketplace (if not already added)
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins

# 2. Install plugin
claude plugin install article-study@jh-claude-plugins
```

### Migrating from blog-digest

If you previously used `blog-digest`:

1. Uninstall the old plugin: `claude plugin uninstall blog-digest`
2. Install the new one: `claude plugin install article-study@jh-claude-plugins`
3. Update your MEMORY.md: rename `## Blog Digest Settings` to `## Article Study Settings`

## Usage

```
블로그 정리해줘 https://example.com/article
```

Also: "article study", "블로그 요약", or any blog/article URL.

## First Run

On first use, the plugin asks you to configure:
1. **Save path** — where to save study notes
   - `article-notes/` in current project (default)
   - Custom absolute path
   - Obsidian vault (see [Obsidian Integration](#obsidian-integration-optional) below)
   - Notion (see [Notion Integration](#notion-integration-optional) below)
2. **Categories** — folder categories for organizing notes (e.g., `tech, business, investing`)
3. **Language** — output language (Korean, English, Japanese, or custom)
4. **Scope** — apply settings globally (all projects) or to the current project only

Settings are stored in MEMORY.md (project-level or global `~/.claude/memory/MEMORY.md`).

## Features

- **No dependencies** — WebFetch-based content extraction, no external tools needed
- **Structured summary** with key points and insights
- **Full translation** to your configured language for foreign-language articles
- **3-level comprehension quiz** (9 questions)
- **Deep Research** follow-up option
- **Output flexibility**: Obsidian / Notion / local file save
- **Configurable** save path, language, and categories

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
    2026-03-08-article-title.md
  investing/
    2026-03-07-another-article.md
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
2. Content extraction (WebFetch)
3. Context gathering (WebSearch)
4. Document generation (summary + insights + full text)
5. Category & file save
6. Study quiz (3 levels x 3 questions)
7. Follow-up (re-quiz / deep research / done)
