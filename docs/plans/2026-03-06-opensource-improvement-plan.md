# Open-Source Repository Improvement Plan

> **Goal:** Bring jh-claude-plugins to full GitHub Community Standards compliance and professional open-source quality.

## Evaluation Rubric

Based on GitHub Community Standards, Open Source Guides (opensource.guide), and Claude Code plugin conventions (code.claude.com/docs/en/plugins).

### Category A: Legal & Governance (필수)

| Item | Weight | Current | Target | Gap |
|------|--------|---------|--------|-----|
| LICENSE file (MIT) | 20 | 0/20 | 20/20 | Missing entirely |
| CODE_OF_CONDUCT.md | 10 | 0/10 | 10/10 | Missing |
| SECURITY.md | 10 | 0/10 | 10/10 | Missing |

### Category B: Developer Experience (필수)

| Item | Weight | Current | Target | Gap |
|------|--------|---------|--------|-----|
| README badges (license) | 5 | 0/5 | 5/5 | No badges |
| README contributing section | 5 | 0/5 | 5/5 | No contributing link |
| README license section | 5 | 0/5 | 5/5 | No license mention |
| CONTRIBUTING.md | 10 | 0/10 | 10/10 | Missing |
| .gitignore | 10 | 0/10 | 10/10 | Missing; .omc/ artifacts at risk |

### Category C: Plugin Metadata (권장)

| Item | Weight | Current | Target | Gap |
|------|--------|---------|--------|-----|
| plugin.json `license` field | 5 | 0/5 | 5/5 | SPDX identifier missing |
| plugin.json `repository` field | 5 | 0/5 | 5/5 | Missing |
| marketplace.json `metadata` | 5 | 0/5 | 5/5 | No metadata block |

### Category D: Community Templates (선택)

| Item | Weight | Current | Target | Gap |
|------|--------|---------|--------|-----|
| Issue templates | 5 | 0/5 | 5/5 | Missing |
| PR template | 5 | 0/5 | 5/5 | Missing |

**Current Score: 0/95 → Target: 95/95**

> Note: marketplace.json `metadata` row removed (Task 8) — field is not part of the documented spec. Rubric total is 95.

---

## Implementation Plan

### Task 1: Create LICENSE (MIT)
- **File**: `/LICENSE`
- **Content**: MIT License with `Copyright (c) 2026 kim-jeonghyun`
- **Source**: https://choosealicense.com/licenses/mit/
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 2: Create .gitignore and untrack .omc/
- **File**: `/.gitignore`
- **Content**: OS artifacts (.DS_Store, Thumbs.db), editor artifacts (.vscode/, .idea/, *.swp), .omc/ state files, .env, node_modules/, *.log
- **Note**: .omc/ directory contains local state files that should not be committed
- **Post-step**: Run `git rm -r --cached .omc/` to stop tracking already-committed .omc/ files
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 3: Create CODE_OF_CONDUCT.md
- **File**: `/CODE_OF_CONDUCT.md`
- **Content**: Contributor Covenant v2.1 (current standard)
- **Source**: https://www.contributor-covenant.org/version/2/1/code_of_conduct/
- **Contact**: GitHub Issues (config-only repo, no email needed)
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 4: Create SECURITY.md
- **File**: `/SECURITY.md`
- **Content**: Minimal policy appropriate for config-only repo. "This repository contains configuration files only and has no runtime code. To report a security concern, use GitHub's private vulnerability reporting feature on this repository."
- **Note**: Do NOT direct security reports to public GitHub issues — use GitHub's built-in private vulnerability reporting
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 5: Create CONTRIBUTING.md (public-facing contributor guide)
- **File**: `/CONTRIBUTING.md`
- **Content**:
  - How to add a new plugin (directory structure, plugin.json, SKILL.md)
  - How to modify existing plugins
  - Commit convention (conventional commits)
  - PR process
  - Link to CODE_OF_CONDUCT.md
- **Role separation**: CONTRIBUTING.md is the public-facing contributor guide for humans. CLAUDE.md is the AI agent-facing project context. Extract these specific CLAUDE.md sections into CONTRIBUTING.md:
  - "Adding a New Plugin" (steps 1-4)
  - "Commit Convention" (types, scope, examples)
  - "Validation & Testing" (validate + install commands)
  Replace those sections in CLAUDE.md with: `See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor guide, commit conventions, and validation commands.`
  Keep in CLAUDE.md: "Structure" (directory tree), "Key Conventions" (agent-relevant rules), "Current Plugins", "Gotchas".
- **Tier**: MEDIUM (requires project-specific content)
- **Dependencies**: Task 1 (LICENSE reference), Task 3 (CoC reference)

### Task 6: Improve README.md
- **File**: `/README.md` (edit existing)
- **Changes**:
  - Add MIT license badge at top
  - Add "Contributing" section with link to CONTRIBUTING.md
  - Add "License" section at bottom
  - Add brief project description/motivation
- **Tier**: MEDIUM (edit existing)
- **Dependencies**: Task 1, Task 5

### Task 7: Update plugin.json metadata
- **File**: `/plugins/blog-digest/.claude-plugin/plugin.json`
- **Changes**:
  - Add `"license": "MIT"` (SPDX identifier)
  - Add `"repository": "https://github.com/kim-jeonghyun/jh-claude-plugins"`
  - Add `"keywords": ["blog", "digest", "study", "quiz", "korean"]`
- **Note**: These fields are additive and not in the minimal required schema. Run `claude plugin validate` after adding to confirm no validation errors. If validation fails, remove the offending fields.
- **Tier**: LOW (JSON field additions)
- **Dependencies**: None

### Task 8: ~~Update marketplace.json metadata~~ REMOVED
- **Reason**: The Claude Code marketplace spec does not define a `metadata` block as a standard convention. The current marketplace.json already has `description` and `owner` at the top level, which is sufficient per official docs. Adding an undocumented `metadata` block could cause validation issues.
- **Rubric impact**: Remove "marketplace.json `metadata`" row from Category C (reduces total from 100 to 95, renormalize).

### Task 9: Create GitHub Issue Templates
- **Files**:
  - `/.github/ISSUE_TEMPLATE/bug_report.md`
  - `/.github/ISSUE_TEMPLATE/feature_request.md`
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 10: Create PR Template
- **File**: `/.github/PULL_REQUEST_TEMPLATE.md`
- **Content**: Checklist for PR submissions (description, testing, conventional commit)
- **Tier**: LOW (boilerplate)
- **Dependencies**: None

### Task 11: Update CLAUDE.md
- **File**: `/CLAUDE.md` (edit existing)
- **Changes**: Add reference to CONTRIBUTING.md, update file structure tree to include new files
- **Tier**: LOW (minor edit)
- **Dependencies**: Tasks 1-10

### Task 12: Commit and verify
- **Action**: Stage all new files, commit with `docs: add open-source community files`
- **Verify**: All files exist and are properly formatted
- **Dependencies**: All tasks complete

---

## Execution Strategy

**Parallel Group 1** (independent, LOW tier): Tasks 1, 2, 3, 4, 7, 9, 10
**Parallel Group 2** (depends on Group 1, MEDIUM tier): Tasks 5, 6
**Sequential** (depends on all): Tasks 11, 12

## Sources

- [GitHub Community Standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories)
- [Best practices for repositories - GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)
- [Open Source Guides](https://opensource.guide/)
- [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)
- [choosealicense.com](https://choosealicense.com/)
- [Claude Code Plugin Docs](https://code.claude.com/docs/en/plugins)
- [Claude Code Plugin Marketplace Docs](https://code.claude.com/docs/en/plugin-marketplaces)
