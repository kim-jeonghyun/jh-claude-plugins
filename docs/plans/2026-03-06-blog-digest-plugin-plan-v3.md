# Blog Digest Plugin Implementation Plan (v3)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Claude Code plugin that extracts blog content, generates study documents with summaries/insights, and tests comprehension with quizzes.

**Architecture:** Monorepo (`jh-claude-plugins`) with `blog-digest` as first plugin. SKILL.md-driven workflow using built-in tools (WebFetch, WebSearch, Write, AskUserQuestion). No external script dependencies. Zero-config default with project MEMORY.md override for custom paths.

**Tech Stack:** Claude Code Plugin System (SKILL.md, plugin.json, references/)

**Commit Convention:** This repo uses conventional commits (`type(scope): message`), not turtle_trading's `[#NNN]` format.

## Execution Context

| Tasks  | Working Directory                     | Notes                             |
| ------ | ------------------------------------- | --------------------------------- |
| 1-5, 7 | `<repo-root>/` (new repo) | All plugin files created here     |
| 6      | Filesystem                            | Dynamic path based on user config |
| 8      | Any Claude Code session               | After plugin installation         |

## Review Changes (v2 -> v3)

| Issue                  | Source        | Fix                                                                                                                              |
| ---------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Idempotency in Task 1  | Agent Council | Added GitHub repo existence check before `gh repo create`                                                                        |
| Idempotency in Task 6  | Agent Council | Added `mkdir -p` check                                                                                                           |
| AskUserQuestion schema | Critic        | Changed 3-question array structure to single question string multi-line format or sequential calls to match standard tool schema |
| Hardcoded Vault Path   | Momus         | Removed hardcoded absolute path in Task 6, linking it to Step 0 dynamic config                                                   |
| Testability of E2E     | Momus         | Clarified Task 8 as a highly interactive manual test sequence                                                                    |

---

### Task 1: Create GitHub Repository

**Files:**

- Create: `<repo-root>/README.md`
- Create: `<repo-root>/.claude-plugin/marketplace.json`

**Step 1: Check repo existence and create public GitHub repo**

```bash
cd ~/dev
if [ ! -d "jh-claude-plugins" ]; then
  gh repo view kim-jeonghyun/jh-claude-plugins >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    gh repo clone kim-jeonghyun/jh-claude-plugins
  else
    gh repo create jh-claude-plugins --public --description "Claude Code plugins for learning and productivity" --clone
  fi
fi
```

**Step 2: Create root README**

Create `<repo-root>/README.md`:

````markdown
# jh-claude-plugins

Claude Code plugins for learning and productivity.

## Plugins

| Plugin                              | Description                            | Version |
| ----------------------------------- | -------------------------------------- | ------- |
| [blog-digest](plugins/blog-digest/) | Blog article digest with study quizzes | 0.1.0   |

## Installation

1. Add marketplace:
   ```bash
   claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
   ```
````

2. Install plugin:
   ```bash
   claude plugin install blog-digest@jh-claude-plugins
   ```

## Author

[kim-jeonghyun](https://github.com/kim-jeonghyun)

````

**Step 3: Create marketplace.json**

Create `<repo-root>/.claude-plugin/marketplace.json`:
```json
{
  "name": "jh-claude-plugins",
  "owner": {
    "name": "kim-jeonghyun",
    "url": "https://github.com/kim-jeonghyun"
  },
  "description": "Claude Code plugins for learning and productivity",
  "plugins": [
    {
      "name": "blog-digest",
      "description": "Blog article digest with summaries, insights, Korean translation, and study quizzes",
      "source": "./plugins/blog-digest"
    }
  ]
}
````

**Step 4: Commit**

```bash
cd <repo-root>
git add README.md .claude-plugin/marketplace.json
git commit -m "init: jh-claude-plugins monorepo with marketplace config" || true
```

**Acceptance Criteria:**

- [ ] `<repo-root>/` exists as git repo
- [ ] `gh repo create` does not fail if repo already exists
- [ ] README has correct 2-step install instructions (marketplace add + plugin install)

---

### Task 2: Create blog-digest Plugin Skeleton

**Files:**

- Create: `plugins/blog-digest/.claude-plugin/plugin.json`
- Create: `plugins/blog-digest/README.md`

**Step 1: Create plugin.json**

Create `<repo-root>/plugins/blog-digest/.claude-plugin/plugin.json`:

```json
{
  "name": "blog-digest",
  "version": "0.1.0",
  "description": "Blog article digest with summaries, insights, Korean translation, and study quizzes",
  "author": {
    "name": "kim-jeonghyun",
    "url": "https://github.com/kim-jeonghyun"
  }
}
```

**Step 2: Create plugin README**

Create `<repo-root>/plugins/blog-digest/README.md`:

```markdown
# Blog Digest

Blog article analysis with summary, insights, Korean translation, and comprehension quizzes.

## Usage

Say "blog digest" or "블로그 정리" followed by a URL.

## First Run

On first use, the plugin asks you to configure:

1. **Save path** - where to save digest files (default: `blog-digests/` in current project, or absolute path for Obsidian)
2. **Categories** - folder categories for organizing digests

Settings are stored in your project's MEMORY.md.

## Features

- WebFetch-based content extraction (no external dependencies)
- Structured summary with insights
- 3-level comprehension quiz (9 questions)
- Deep Research follow-up option
- Configurable save path and categories

## Workflow

1. Config check (first run: setup wizard)
2. Content extraction (WebFetch)
3. Context gathering (WebSearch)
4. Document generation (summary + insights + full text)
5. File save
6. Study quiz (3 levels x 3 questions)
7. Follow-up (re-quiz / deep research / done)
```

**Step 3: Commit**

```bash
cd <repo-root>
git add plugins/blog-digest/
git commit -m "feat(blog-digest): add plugin skeleton with plugin.json and README" || true
```

**Acceptance Criteria:**

- [ ] plugin.json matches expected schema pattern
- [ ] README documents first-run onboarding flow

---

### Task 3: Create SKILL.md (Core Workflow)

**Step 1: Write SKILL.md**

Create `<repo-root>/plugins/blog-digest/skills/blog-digest/SKILL.md`:

## ` ` `markdown

name: blog-digest
description: Digest a blog article into a structured study document with comprehension quizzes. Triggers on "블로그 정리", "blog digest", or blog URL.

---

# Blog Digest

Blog article -> structured study document -> comprehension quiz.

## Workflow

### 0. Configuration Check

Check project MEMORY.md for `blog-digest` config section. If not found, run setup:

1. AskUserQuestion: "Where should blog digests be saved?"
   - Options: "Current project (blog-digests/)" / "Custom path (e.g., Obsidian vault)"
   - If custom/Obsidian: ask for absolute path
2. AskUserQuestion: "What categories do you want for organizing digests?"
   - Offer text input for comma-separated category names
   - Example: "tech, business, investing, science, opinion"
3. Save config to project MEMORY.md under `## Blog Digest Settings`:

```
## Blog Digest Settings
- **Save path**: {chosen path}
- **Categories**: {comma-separated list}
```

If config exists, read it and proceed.

### 1-5. Content Extraction, Gathering, Document Generation, File Save

(Execute standard steps using WebFetch, WebSearch, summarize with insights, and write file to `{save path}/{category}/YYYY-MM-DD-{sanitized-title}.md`.)

#### Content Extraction Fallback

If WebFetch returns incomplete content:
Wait and retry, or use AskUserQuestion to ask the user to provide the raw text if blocked.

**Duplicate check**: If file already exists at target path, AskUserQuestion: Overwrite, Save with suffix, or Skip.

### 6. Study Quiz

3 levels x 3 questions = 9 total.
**IMPORTANT**: Claude's `AskUserQuestion` tool often supports just simple strings. Ask questions sequentially (9 calls) OR generate a single multi-line text prompt displaying 3 questions at once and ask the user to reply with 3 answers (e.g., "1:A, 2:B, 3:C").

Question format details: `references/quiz-patterns.md`

#### Result Processing

After wrong answers, provide correct answer with explanation. Append quiz results to document:

```
## Quiz Results

Score: 7/9 (78%) | Level 1: 3/3 | Level 2: 2/3 | Level 3: 2/3
```

### 7. Follow-up

AskUserQuestion: "Re-quiz, Deep Research, or Done?"
` ` `

**Step 2: Commit**

```bash
cd <repo-root>
git add plugins/blog-digest/skills/
git commit -m "feat(blog-digest): add SKILL.md with config-driven 8-step workflow" || true
```

**Acceptance Criteria:**

- [ ] No hardcoded absolute paths in SKILL.md
- [ ] Step 0 onboarding flow defined
- [ ] Duplicate file check included
- [ ] Quiz execution handles `AskUserQuestion` schema safely without assuming complex arrays

---

### Task 4: Create Quiz Patterns Reference

**Files:**

- Create: `plugins/blog-digest/skills/blog-digest/references/quiz-patterns.md`

**Step 1: Write quiz-patterns.md**

Create `<repo-root>/plugins/blog-digest/skills/blog-digest/references/quiz-patterns.md`:

````markdown
# Quiz Patterns

3-level quiz guide for blog digest comprehension testing.

## Question Types by Level

### Level 1 (Basic) - Insight Comprehension

Verify understanding of core message and key concepts.

### Level 2 (Intermediate) - Insight-Detail Connection

Verify relationships between concepts and supporting evidence.

### Level 3 (Advanced) - Detail & Application

Case analysis and specific data.

## AskUserQuestion Format

Use `AskUserQuestion` by passing a formatted string containing the questions for that level, e.g.:

```text
Please answer the following 3 questions for Level 1 (Basic):

Q1. What is the core message of this article?
A) Option A
B) Option B
C) Option C

Q2. What principle did the author emphasize most?
...

Please reply with your answers (e.g., 1:A, 2:B, 3:C).
```
````

## Result Processing

After each level:

1. Show correct/incorrect immediately
2. For wrong answers, provide detailed explanation:
   - What the correct answer is
   - Why it is correct (reference article content)
   - Relevant section of the article

````

**Step 2: Commit**

```bash
cd <repo-root>
git add plugins/blog-digest/skills/blog-digest/references/quiz-patterns.md
git commit -m "feat(blog-digest): add quiz patterns reference" || true
````

**Acceptance Criteria:**

- [ ] quiz-patterns.md covers all 3 levels (Basic, Intermediate, Advanced)
- [ ] AskUserQuestion format explicitly uses a standard text prompt, avoiding proprietary unsupported JSON schemas.

---

### Task 5: Create Deep Research Reference

**Files:**

- Create: `plugins/blog-digest/skills/blog-digest/references/deep-research.md`

(Create the file matching the content from the previous v2 plan, maintaining the 5-search, 3-fetch limits and append logic).

**Acceptance Criteria:**

- [ ] deep-research.md includes search cap and document extension template.

---

### Task 6: Validate, Push, and Install Plugin

**Step 1: Validate plugin manifest**

```bash
claude plugin validate <repo-root>/plugins/blog-digest
```

Expected: Validation passes with no errors. Fix if failed.

**Step 2: Push to GitHub**

```bash
cd <repo-root>
git push -u origin main
```

**Step 3: Add marketplace & Install**

```bash
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
claude plugin install blog-digest@jh-claude-plugins
```

**Acceptance Criteria:**

- [ ] `claude plugin validate` passes
- [ ] Plugin appears in `claude plugin list`

---

### Task 7: End-to-End Manual Test

_This task is to be executed interactively by a human user or an agent with exact prompt automation._

**Step 1: Test with a URL**

In a new Claude Code session, say:

```
블로그 정리 https://intellectia.ai/blog/how-will-openclaw-affect-your-investment-journey
```

**Step 2: Verify workflow manually**

Checklist:

- [ ] Step 0 wizard triggers and saves to `MEMORY.md`.
- [ ] Document correctly generated in the specified directory.
- [ ] Quiz format is readable and accepts user string response.

**Step 3: Verify idempotency (second run)**
Run with a different URL, verify the wizard skips setup.

**Acceptance Criteria:**

- [ ] All interactive flows complete without crashing or schema errors.
