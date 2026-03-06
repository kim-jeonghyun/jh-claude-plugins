# YouTube Digest v2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fork and improve the youtube-digest plugin with adaptive templates, 2-pass analysis, and topic segmentation for long videos.

**Architecture:** Layered Enhancement of team-attention-plugins youtube-digest (MIT). Add Step 1.5 (strategy) + Step 2.5 (segmentation) to existing 8-step workflow. Shared references with blog-digest in jh-claude-plugins monorepo.

**Tech Stack:** Claude Code Plugin System (SKILL.md, plugin.json, references/, bash scripts)

**Commit Convention:** `type(scope): message` (jh-claude-plugins convention)

**Design Doc:** `docs/plans/2026-03-06-youtube-digest-v2-design.md`

## Execution Context

| Tasks | Working Directory | Notes |
|-------|-------------------|-------|
| 1-8 | `<repo-root>/` | All plugin files |
| 9 | Any Claude Code session | After plugin installation |

---

### Task 1: Create shared/ references (extract from blog-digest)

**Files:**
- Move: `plugins/blog-digest/skills/blog-digest/references/quiz-patterns.md` -> `shared/quiz-patterns.md`
- Move: `plugins/blog-digest/skills/blog-digest/references/deep-research.md` -> `shared/deep-research.md`
- Create: `shared/category-config.md`
- Create: `shared/output-save.md`

**Step 1: Move quiz-patterns.md to shared/**

```bash
cd <repo-root>
mkdir -p shared
git mv plugins/blog-digest/skills/blog-digest/references/quiz-patterns.md shared/quiz-patterns.md
```

**Step 2: Move deep-research.md to shared/**

```bash
git mv plugins/blog-digest/skills/blog-digest/references/deep-research.md shared/deep-research.md
```

**Step 3: Create shared/category-config.md**

```markdown
# Category Configuration

## Onboarding (first run)

If no category config exists in MEMORY.md, ask via AskUserQuestion:
"What categories do you want for organizing content?"

Provide text input for comma-separated category names.
Save to MEMORY.md under the plugin's settings section.

## Classification Workflow

1. Analyze content and suggest category from user's configured list
2. If clear match: use directly
3. If ambiguous: present top 2-3 options via AskUserQuestion
4. If no match: offer to create new category (update MEMORY.md)

## Default Category Examples

Investment-focused:
- chart_analysis, risk_management, macro, value_investing, trading_psychology, strategy

Tech-focused:
- engineering, product, ai-ml, devops, architecture, career

General:
- tech, business, investing, science, opinion, lifestyle
```

**Step 4: Create shared/output-save.md**

```markdown
# Output Save Configuration

## Save Targets

| Target | Config Key | Behavior |
|--------|-----------|----------|
| Obsidian | `save_path: /absolute/path/to/vault/` | Write .md directly |
| Notion | `save_target: notion` | Generate document, inform user to copy-paste |
| Local | `save_path: ./digests/` | Save relative to current project |

## Configuration Priority

1. Check MEMORY.md for `save_path` or `save_target` -> use if found
2. If not found -> first-run AskUserQuestion:
   - "Where should documents be saved?"
   - Options: "Current project (digests/)" / "Custom path" / "Obsidian vault"
   - If custom/Obsidian: ask for absolute path
3. Save choice to MEMORY.md

## Notion Handling

Notion cannot be written to directly via Write tool.
When `save_target: notion`:
1. Generate the full document as normal
2. Display: "Document ready. Copy the content above and paste into Notion."
3. Skip file write step
4. (Future: Notion MCP server integration for auto-save)

## Duplicate Check

Before saving, check if file already exists at target path.
If duplicate found, ask user via AskUserQuestion:
- Overwrite existing file
- Save with suffix (e.g., `-2`)
- Skip saving
```

**Step 5: Remove empty references/ directory if blog-digest references are gone**

```bash
rmdir plugins/blog-digest/skills/blog-digest/references/ 2>/dev/null || true
```

**Step 6: Commit**

```bash
git add shared/ plugins/blog-digest/skills/blog-digest/references/
git commit -m "refactor(shared): extract common references from blog-digest

Move quiz-patterns.md and deep-research.md to shared/.
Add category-config.md and output-save.md for cross-plugin reuse."
```

---

### Task 2: Update blog-digest to reference shared/

**Files:**
- Modify: `plugins/blog-digest/skills/blog-digest/SKILL.md`

**Step 1: Update quiz-patterns reference path**

In SKILL.md, replace:
```
Question format details: `references/quiz-patterns.md`
```
With:
```
Question format details: `../../../shared/quiz-patterns.md`
```

**Step 2: Update deep-research reference path**

In SKILL.md, replace:
```
- **Deep Research**: Web deep-dive (`references/deep-research.md`)
```
With:
```
- **Deep Research**: Web deep-dive (`../../../shared/deep-research.md`)
```

**Step 3: Verify no other references/ paths remain**

```bash
grep -n "references/" plugins/blog-digest/skills/blog-digest/SKILL.md
```

Expected: no matches.

**Step 4: Commit**

```bash
git add plugins/blog-digest/skills/blog-digest/SKILL.md
git commit -m "refactor(blog-digest): point references to shared/"
```

---

### Task 3: Create youtube-digest plugin skeleton

**Files:**
- Create: `plugins/youtube-digest/.claude-plugin/plugin.json`
- Create: `plugins/youtube-digest/LICENSE.original`
- Create: `plugins/youtube-digest/README.md`
- Create: `NOTICE` (repo root)

**Step 1: Create plugin.json**

```bash
mkdir -p plugins/youtube-digest/.claude-plugin
```

```json
{
  "name": "youtube-digest",
  "version": "1.0.0",
  "description": "YouTube video digest with adaptive templates, topic segmentation, and study quizzes",
  "author": {
    "name": "kim-jeonghyun",
    "url": "https://github.com/kim-jeonghyun"
  },
  "license": "MIT",
  "repository": "https://github.com/kim-jeonghyun/jh-claude-plugins",
  "keywords": ["youtube", "digest", "study", "quiz", "korean", "transcript"]
}
```

**Step 2: Create LICENSE.original**

Copy the full MIT License text from team-attention-plugins:

```
MIT License

Copyright (c) 2025 Team Attention

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Step 3: Create README.md**

```markdown
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

```bash
brew install yt-dlp
```

## Usage

```
유튜브 정리해줘 https://www.youtube.com/watch?v=xxxxx
```

Also: "영상 요약", "transcript 번역", "YouTube digest", "영상 퀴즈"
```

**Step 4: Create NOTICE at repo root**

```
NOTICES AND ATTRIBUTIONS

youtube-digest is based on youtube-digest from team-attention-plugins.
Copyright (c) 2025 Team Attention
Licensed under the MIT License.
See plugins/youtube-digest/LICENSE.original for the full license text.
Original source: https://github.com/team-attention/claude-plugins
```

**Step 5: Commit**

```bash
git add plugins/youtube-digest/.claude-plugin/ plugins/youtube-digest/LICENSE.original \
  plugins/youtube-digest/README.md NOTICE
git commit -m "feat(youtube-digest): add plugin skeleton with attribution

Fork of team-attention-plugins youtube-digest (MIT License).
Includes LICENSE.original and NOTICE for proper attribution."
```

---

### Task 4: Create scripts (metadata + transcript extraction)

**Files:**
- Create: `plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh`
- Create: `plugins/youtube-digest/skills/youtube-digest/scripts/extract_transcript.sh`

**Step 1: Create extract_metadata.sh**

Copy from original (unchanged):

```bash
#!/bin/bash
# YouTube metadata extraction
# Usage: ./extract_metadata.sh <URL>

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: $0 <YouTube URL>"
  exit 1
fi

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
```

> Note: Added `duration_seconds` (integer) for preset calculation and `is_live` for live stream detection. These were missing in the original.

**Step 2: Create extract_transcript.sh (bug fix applied)**

```bash
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
```

> Bug fix: `--convert-subs json3` -> `--sub-format srt`. Also simplified output filename to `yt_transcript` for predictable path.

**Step 3: Make scripts executable**

```bash
chmod +x plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh
chmod +x plugins/youtube-digest/skills/youtube-digest/scripts/extract_transcript.sh
```

**Step 4: Verify scripts run (dry check)**

```bash
# Check syntax only (no actual download)
bash -n plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh
bash -n plugins/youtube-digest/skills/youtube-digest/scripts/extract_transcript.sh
echo "Both scripts pass syntax check"
```

Expected: "Both scripts pass syntax check"

**Step 5: Commit**

```bash
git add plugins/youtube-digest/skills/youtube-digest/scripts/
git commit -m "feat(youtube-digest): add metadata and transcript extraction scripts

Bug fix: use --sub-format srt instead of broken --convert-subs json3.
Add duration_seconds and is_live to metadata output."
```

---

### Task 5: Create adaptive templates

**Files:**
- Create: `plugins/youtube-digest/skills/youtube-digest/references/templates/short.md`
- Create: `plugins/youtube-digest/skills/youtube-digest/references/templates/medium.md`
- Create: `plugins/youtube-digest/skills/youtube-digest/references/templates/long.md`

**Step 1: Create short.md (videos under 30 minutes)**

```markdown
# SHORT Template (under 30 minutes)

## Output Structure

~~~
---
title: {video title}
url: {YouTube URL}
channel: {channel name}
date: {upload date}
duration: {video length}
preset: SHORT
processed_at: {processing datetime}
---

# {video title}

## Summary
{3-5 sentence summary}

### Key Points
1. {point 1}
2. {point 2}
3. {point 3}

## Insights

### Core Ideas
{deep analysis of main arguments}

### Applicable Points
{practical takeaways}

## Full Script (Korean)
[00:00] ...
[00:15] ...
~~~

## Guidelines
- Full transcript translation included
- Single-pass analysis (no segmentation needed)
- 3-5 sentence summary with 3 key points
```

**Step 2: Create medium.md (30 minutes to 2 hours)**

```markdown
# MEDIUM Template (30 minutes to 2 hours)

## Output Structure

~~~
---
title: {video title}
url: {YouTube URL}
channel: {channel name}
date: {upload date}
duration: {video length}
preset: MEDIUM
processed_at: {processing datetime}
---

# {video title}

## Summary
{5-8 sentence summary}

### Key Points
1. {point 1}
2. {point 2}
3. {point 3}
4. {point 4}
5. {point 5}

## Part 1: {topic title} [{start}~{end}]

### Key Arguments
{core claims and reasoning}

### Details
{supporting evidence, examples, data}

### Insights
{analysis and takeaways for this part}

## Part 2: {topic title} [{start}~{end}]
...

## Part N: ...

## Key Quotes
| Time | Quote |
|------|-------|
| [MM:SS] | "notable quote" |

## Quiz Results
(recorded after quiz)
~~~

## Guidelines
- 2-pass analysis required (Pass 1: TOC, Pass 2: per-part analysis)
- Typically 3-6 parts
- Key quotes instead of full transcript (10-15 notable quotes with timestamps)
- 5-8 sentence summary with 5 key points
```

**Step 3: Create long.md (over 2 hours)**

```markdown
# LONG Template (over 2 hours)

## Output Structure

~~~
---
title: {video title}
url: {YouTube URL}
channel: {channel name}
date: {upload date}
duration: {video length}
preset: LONG
processed_at: {processing datetime}
---

# {video title}

## Summary
{8-12 sentence summary}

### Key Points
1. {point 1}
2. {point 2}
3. {point 3}
4. {point 4}
5. {point 5}
6. {point 6}
7. {point 7}

## Part 1: {topic title} [{start}~{end}]

### Key Arguments
{core claims and reasoning}

### Details
{supporting evidence, examples, context}

### Data & Figures
{specific numbers, statistics, comparisons mentioned}

### Insights
{analysis and takeaways for this part}

## Part 2: {topic title} [{start}~{end}]
...

## Part N: ...

## Cross-Part Analysis
{connections between parts, overarching themes, contradictions}

## Key Quotes
| Time | Quote |
|------|-------|
| [MM:SS] | "notable quote" |

## Quiz Results
(recorded after quiz)
~~~

## Guidelines
- 2-pass analysis required (Pass 1: TOC, Pass 2: per-part analysis)
- Typically 6-10 parts
- Each part includes Data & Figures section
- Cross-Part Analysis section for synthesis across topics
- Key quotes instead of full transcript (15-25 notable quotes with timestamps)
- 8-12 sentence summary with 7 key points
```

**Step 4: Commit**

```bash
git add plugins/youtube-digest/skills/youtube-digest/references/
git commit -m "feat(youtube-digest): add adaptive templates for SHORT/MEDIUM/LONG

SHORT (<30min): full transcript, 3-5 sentence summary.
MEDIUM (30min-2h): part-based analysis, key quotes.
LONG (2h+): part-based with data/figures and cross-part analysis."
```

---

### Task 6: Update shared/quiz-patterns.md with scaling rules

**Files:**
- Modify: `shared/quiz-patterns.md`

**Step 1: Add scaling section to quiz-patterns.md**

Append after the existing "Result Processing" section:

```markdown

## Quiz Scaling by Content Length

| Preset | Questions | Structure | AskUserQuestion Calls |
|--------|-----------|-----------|----------------------|
| SHORT / short content | 9 | 3 levels x 3 questions | 3 (1 per level) |
| MEDIUM / medium content | 9 | 3 levels x 3 questions (distribute across parts) | 3 |
| LONG / long content | 12-15 | 3 levels x 4-5 questions | 6 (2 per level) |

### LONG Content Quiz Rules

- AskUserQuestion supports max 4 questions per call
- Split each level into 2 calls: first 2-3 questions, then remaining 2 questions
- Ensure every part/section gets at least 1 question across all levels
- Distribute questions proportionally to part importance/length

### Part Coverage

When content has multiple parts/sections:
1. Map each question to a specific part
2. Verify all parts are covered by at least 1 question
3. If parts > questions in a level, prioritize parts with most substantive content
```

**Step 2: Commit**

```bash
git add shared/quiz-patterns.md
git commit -m "feat(shared): add quiz scaling rules for long content

LONG preset gets 12-15 questions across 6 AskUserQuestion calls.
Part coverage guarantee ensures all sections are tested."
```

---

### Task 7: Create the main SKILL.md

**Files:**
- Create: `plugins/youtube-digest/skills/youtube-digest/SKILL.md`

**Step 1: Write SKILL.md**

This is the core deliverable. Full content:

```markdown
---
name: youtube-digest
description: YouTube video digest with adaptive depth. Triggers on "유튜브 정리", "영상 요약", "transcript 번역", "YouTube digest", "영상 퀴즈", or YouTube URL.
---

# YouTube Digest v2

YouTube video analysis with adaptive depth based on video length.

## Workflow

### 1. Metadata Extraction

```bash
scripts/extract_metadata.sh "<URL>"
```

Extract: title, channel, upload_date, duration, duration_seconds, tags, is_live.

If `is_live` is true, inform user: "Live stream is still in progress. Please try again after it ends." and stop.

### 1.5. Processing Strategy

Determine preset from `duration_seconds`:

| Preset | Duration | Template | Transcript Output | Quiz |
|--------|----------|----------|-------------------|------|
| SHORT  | < 1800s (~30min) | `references/templates/short.md` | Full translation | 9 (3x3) |
| MEDIUM | 1800-7200s (30min-2h) | `references/templates/medium.md` | Key quotes | 9 (3x3) |
| LONG   | > 7200s (2h+) | `references/templates/long.md` | Key quotes | 12-15 (4-5 x 3) |

Announce to user: "This is a {preset} video ({duration}). Using {preset} analysis template."

### 2. Transcript Extraction

```bash
scripts/extract_transcript.sh "<URL>" [output_dir]
```

Priority: manual subtitles (ko > en) > auto-generated (ko > en).

If no subtitles available: inform user and stop.

### 2.5. Topic Segmentation (MEDIUM/LONG only)

SHORT videos skip this step entirely.

**Pass 1 - Table of Contents:**

Read transcript in chunks (~3000 lines per read, reduce to ~2000 if context issues).
While reading, identify topic transitions:
- Explicit markers: "다음으로", "자 이제", "두번째로", new question from audience
- Implicit markers: sudden topic change, long pause indicators, new speaker

Produce a numbered TOC:
```
Part 1 [00:00~15:30] Opening & Market Overview
Part 2 [15:30~35:20] Topic A Analysis
Part 3 [35:20~55:00] Topic B Deep Dive
...
```

**Pass 2 - Per-Part Analysis:**

For each part, re-read the relevant transcript section and analyze:
- Core arguments and reasoning
- Specific data, numbers, statistics mentioned
- Notable quotes with timestamps
- Insights and takeaways

### 3. Context Gathering (WebSearch)

Web search for proper nouns and domain context:
- `"{video title}" {channel} summary`
- `"{speaker}" {topic keywords}`

### 4. Transcript Correction

Replace auto-subtitle misrecognitions with correct terms from web search:
- Proper nouns, technical terms, brand names
- Mark genuinely unclear sections with `[unclear]`

### 5. Document Generation

Load the template for the determined preset: `references/templates/{preset}.md`

Generate the document following the template structure exactly.
Fill all sections with analysis from Steps 2.5 and 3-4.

### 6. File Save

Refer to `../../../shared/output-save.md` for save target configuration.
Refer to `../../../shared/category-config.md` for category classification.

Save path: `{configured_path}/{category}/{YYYY-MM-DD}-{sanitized-title}.md`

Sanitization: lowercase, spaces to hyphens, remove special chars except hyphens, max 60 chars.

### 7. Study Quiz

Refer to `../../../shared/quiz-patterns.md` for question patterns and scaling rules.

| Preset | Questions | Calls |
|--------|-----------|-------|
| SHORT  | 9 (3x3) | 3 |
| MEDIUM | 9 (3x3, distributed across parts) | 3 |
| LONG   | 12-15 (4-5 x 3) | 6 |

After grading, append quiz results to the saved document:

```
## Quiz Results

Score: 7/9 (78%) | Level 1: 3/3 | Level 2: 2/3 | Level 3: 2/3

### Wrong Answer Notes

**Q5**: {question}
- Selected: B -> Correct: C
- {1-2 sentence explanation}
```

### 8. Follow-up

After quiz, ask via AskUserQuestion:
- **Re-quiz**: Test again with different questions
- **Deep Research**: Web deep-dive (`../../../shared/deep-research.md`)
- **Done**: Finish

## Error Handling

| Situation | Response |
|-----------|----------|
| No subtitles | "Cannot extract subtitles." -> stop |
| Very low quality subtitles | Use `[unclear]` markers, supplement with web search |
| Live stream in progress | "Still live. Try after it ends." -> stop |
| yt-dlp not installed | "Install with: brew install yt-dlp" -> stop |
| Transcript exceeds context | Reduce chunk size (3000 -> 2000 lines) |
| Save path inaccessible | Error message + suggest alternative path |

## Subtitle Language Priority

1. Korean manual -> 2. English manual -> 3. Korean auto -> 4. English auto

## Resources

- `scripts/extract_metadata.sh` - metadata extraction
- `scripts/extract_transcript.sh` - subtitle extraction (SRT)
- `references/templates/short.md` - SHORT preset template
- `references/templates/medium.md` - MEDIUM preset template
- `references/templates/long.md` - LONG preset template
- `../../../shared/quiz-patterns.md` - quiz patterns + scaling
- `../../../shared/deep-research.md` - Deep Research workflow
- `../../../shared/category-config.md` - category classification
- `../../../shared/output-save.md` - save target configuration
```

**Step 2: Commit**

```bash
git add plugins/youtube-digest/skills/youtube-digest/SKILL.md
git commit -m "feat(youtube-digest): add SKILL.md with adaptive workflow

Layered enhancement: Steps 1.5 (preset selection) and 2.5 (topic segmentation).
SHORT/MEDIUM/LONG presets with scaled templates and quiz coverage."
```

---

### Task 8: Update marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Add youtube-digest to plugins array**

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
    },
    {
      "name": "youtube-digest",
      "description": "YouTube video digest with adaptive depth, topic segmentation, and study quizzes",
      "source": "./plugins/youtube-digest"
    }
  ]
}
```

**Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('Valid JSON')"
```

Expected: "Valid JSON"

**Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): register youtube-digest plugin"
```

---

### Task 9: End-to-End Verification

**Step 1: Verify directory structure**

```bash
cd <repo-root>
find plugins/youtube-digest -type f | sort
```

Expected output:
```
plugins/youtube-digest/.claude-plugin/plugin.json
plugins/youtube-digest/LICENSE.original
plugins/youtube-digest/README.md
plugins/youtube-digest/skills/youtube-digest/SKILL.md
plugins/youtube-digest/skills/youtube-digest/references/templates/long.md
plugins/youtube-digest/skills/youtube-digest/references/templates/medium.md
plugins/youtube-digest/skills/youtube-digest/references/templates/short.md
plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh
plugins/youtube-digest/skills/youtube-digest/scripts/extract_transcript.sh
```

**Step 2: Verify shared/ exists and blog-digest references are gone**

```bash
ls shared/
ls plugins/blog-digest/skills/blog-digest/references/ 2>/dev/null && echo "FAIL: references dir should not exist" || echo "PASS: references dir removed"
```

Expected:
```
category-config.md  deep-research.md  output-save.md  quiz-patterns.md
PASS: references dir removed
```

**Step 3: Verify blog-digest SKILL.md references shared/**

```bash
grep "shared/" plugins/blog-digest/skills/blog-digest/SKILL.md
```

Expected: 2 matches (quiz-patterns and deep-research paths).

**Step 4: Verify all JSON files are valid**

```bash
for f in .claude-plugin/marketplace.json plugins/youtube-digest/.claude-plugin/plugin.json plugins/blog-digest/.claude-plugin/plugin.json; do
  python3 -c "import json; json.load(open('$f')); print(f'OK: $f')"
done
```

Expected: 3 "OK" lines.

**Step 5: Verify scripts are executable**

```bash
test -x plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh && echo "metadata: executable" || echo "metadata: NOT executable"
test -x plugins/youtube-digest/skills/youtube-digest/scripts/extract_transcript.sh && echo "transcript: executable" || echo "transcript: NOT executable"
```

Expected: both "executable".

**Step 6: Functional test with a short video (optional, requires yt-dlp)**

```bash
# Quick metadata test with a known short video
plugins/youtube-digest/skills/youtube-digest/scripts/extract_metadata.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 2>/dev/null | head -5
```

Expected: title, channel, upload_date, duration, duration_seconds fields printed.

**Step 7: Push to remote**

```bash
git push origin main
```

---

## Acceptance Criteria

- [ ] `shared/` contains 4 files (quiz-patterns, deep-research, category-config, output-save)
- [ ] blog-digest references `shared/` instead of local `references/`
- [ ] youtube-digest plugin skeleton complete (plugin.json, LICENSE.original, README, NOTICE)
- [ ] `extract_transcript.sh` uses `--sub-format srt` (not `--convert-subs json3`)
- [ ] `extract_metadata.sh` outputs `duration_seconds` and `is_live`
- [ ] 3 adaptive templates exist (short.md, medium.md, long.md)
- [ ] SKILL.md includes Steps 1.5 and 2.5 with preset-based branching
- [ ] quiz-patterns.md includes scaling rules for LONG content
- [ ] marketplace.json lists both blog-digest and youtube-digest
- [ ] All JSON files pass validation
- [ ] All scripts are executable
