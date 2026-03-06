# Post-Review Improvement Plan (v2)

> **Date:** 2026-03-06
> **Source:** 6-reviewer Opus consensus review (unanimous APPROVE with improvement items)
> **Branch:** main (GitHub Flow, direct commits)
> **Revision:** v2 — addresses Critic REJECT feedback (5 critical findings)

---

## Context

Six Opus reviewers approved the jh-claude-plugins repo but identified 10 improvement items across HIGH/MEDIUM/LOW priority. This plan addresses all actionable items in dependency order. Item #9 (additional badges) is intentionally deferred as purely cosmetic.

## Work Objectives

1. Fix HIGH-priority issues that affect correctness and GitHub auto-detection
2. Clean up MEDIUM-priority git hygiene and documentation issues
3. Add LOW-priority CI and developer experience improvements

## Guardrails

**Must Have:**
- All HIGH items resolved before merging any LOW items
- Each logical change is a separate conventional commit
- No runtime code (config-only repo convention)
- SKILL.md description must be under 120 characters after fix

**Must NOT Have:**
- Hardcoded user paths (`<repo-root>`) in any committed file
- Reference-style CODE_OF_CONDUCT.md (must contain full CC v2.1 text)
- Force pushes or history rewrites

---

## Task Flow

```
Phase 1 (parallel):   [T1: CoC full text]  [T2: SKILL.md description]
Phase 2 (sequential): [T4: Fix hardcoded paths] -> [T3: Commit plan docs]
Phase 3 (parallel):   [T5: README + config] [T6: CI workflow]
Phase 4 (manual):     [T7: blog-digest E2E test — separate session, post-push]
```

- Phase 1: T1 and T2 are fully independent, parallel safe.
- Phase 2: T4 MUST complete before T3 (fix paths first, then commit clean files).
- Phase 3: T5 and T6 are independent, parallel safe.
- Phase 4: T7 requires a separate Claude Code session with the plugin installed. Deferred to post-push.

---

## Detailed TODOs

### T1: Replace CODE_OF_CONDUCT.md with full Contributor Covenant v2.1 text [HIGH]

**Why:** GitHub's Community Profile auto-detection looks for specific headings ("Our Pledge", "Our Standards", "Enforcement Guidelines"). The current reference-style CoC (18 lines) has a 60-70% chance of failing detection.

**Approach:**
- Use `curl` to download the full CC v2.1 markdown:
  ```bash
  curl -sL https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md -o CODE_OF_CONDUCT.md
  ```
- After download, replace the `[INSERT CONTACT METHOD]` placeholder with: `via [GitHub's private reporting](https://docs.github.com/en/communities/maintaining-your-safety-on-github/reporting-abuse-or-spam)`
- **Do NOT attempt to generate the full text from memory** — previous session hit content filter.

**Fallback (if canonical URL fails):**
1. Try GitHub mirror: `https://raw.githubusercontent.com/EthicalSource/contributor_covenant/release/content/version/2/1/code_of_conduct.md`
2. Try copy from well-known repo: `curl -sL https://raw.githubusercontent.com/github/docs/main/CODE_OF_CONDUCT.md`
3. Last resort: keep reference-style and note as manual post-push fix

**Acceptance Criteria:**
- [ ] `CODE_OF_CONDUCT.md` contains "Our Pledge", "Our Standards", "Our Responsibilities" headings
- [ ] Contact method replaced (no `[INSERT CONTACT METHOD]` placeholder)
- [ ] File is > 50 lines (full text, not a summary)

**Commit:** `docs: replace CoC with full Contributor Covenant v2.1 text`

---

### T2: Shorten SKILL.md description to under 120 characters [HIGH]

**Why:** Current description is 132 characters (142 bytes UTF-8), exceeding the 120-character limit specified in CLAUDE.md conventions. The 120-char limit is measured in characters, not bytes.

**Current (132 chars):** `Digest a blog article into a structured study document with comprehension quizzes. Triggers on "블로그 정리", "blog digest", or blog URL.`

**Replacement (82 chars):** `Digest a blog article into a structured study document with comprehension quizzes.`

The trigger information ("블로그 정리", "blog digest", blog URL) is already documented in the SKILL.md body and does not need to be in the description frontmatter.

**File:** `plugins/blog-digest/skills/blog-digest/SKILL.md` (line 3, frontmatter `description` field)

**Acceptance Criteria:**
- [ ] Description is under 120 characters (verify with `echo -n "..." | wc -m`)
- [ ] Description still accurately conveys the skill's purpose
- [ ] No other frontmatter fields changed

**Commit:** `fix(blog-digest): shorten SKILL.md description to under 120 chars`

---

### T4: Remove hardcoded paths from plan docs [MEDIUM]

**Why:** Multiple plan docs contain `<repo-root>` which is a user-specific path.

**Approach:**
- Search all files in `docs/plans/` for `<repo-root>`
- Replace with relative reference or generic `<repo-root>` placeholder
- Since these are historical plan docs (not executable scripts), `<repo-root>` is acceptable
- **This task MUST complete before T3** so committed files are clean

**Affected files (including this plan itself):**
- `docs/plans/2026-03-06-blog-digest-plugin-plan-v2.md` (30+ occurrences)
- `docs/plans/2026-03-06-blog-digest-plugin-plan-v3.md` (18 occurrences)
- `docs/plans/2026-03-06-opensource-completion-plan.md` (2 occurrences)
- `docs/plans/2026-03-06-youtube-digest-v2-plan.md` (3 occurrences)
- `docs/plans/2026-03-06-youtube-digest-v2-design.md` (1 occurrence)
- `docs/plans/2026-03-06-post-review-improvement-plan.md` (this file — 0 after v2 rewrite)

**Acceptance Criteria:**
- [ ] `grep -r "<repo-root>" docs/plans/` returns zero results
- [ ] Plan docs remain readable with the replacement paths

---

### T3: Commit untracked plan docs [MEDIUM]

**Depends on:** T4 (paths must be clean first)

**Why:** 6 untracked files and 1 modified file in working tree need to be committed.

**Files to stage and commit:**
- `docs/plans/2026-03-05-blog-digest-plugin-design.md` (untracked)
- `docs/plans/2026-03-06-blog-digest-plugin-plan-v2.md` (modified)
- `docs/plans/2026-03-06-blog-digest-plugin-plan-v3.md` (untracked)
- `docs/plans/2026-03-06-youtube-digest-v2-design.md` (untracked)
- `docs/plans/2026-03-06-youtube-digest-v2-plan.md` (untracked)
- `docs/plans/2026-03-06-implementation-review-report.md` (untracked)
- `docs/plans/2026-03-06-post-review-improvement-plan.md` (untracked, this file)

**Acceptance Criteria:**
- [ ] All 7 files committed
- [ ] `git status` shows clean working tree for `docs/plans/`

**Commit:** `docs: add development plan docs and review report` (combined with T4 path fixes)

---

### T5: README enhancement + issue template config + docs/plans policy [LOW]

**Why:** Three small improvements bundled into one commit.

**T5a: README "What are Claude Code plugins?" explanation**
- Add 2-3 sentences after the description explaining what Claude Code plugins are
- Keep concise: SKILL.md-driven, config-only, no runtime code

**T5b: Issue template config.yml**
- Create `.github/ISSUE_TEMPLATE/config.yml`:
  ```yaml
  blank_issues_enabled: true
  ```

**T5c: Clarify docs/plans/ policy in CLAUDE.md**
- Change: `docs/plans/                       # Implementation plans (not shipped)`
- To: `docs/plans/                       # Development plans (committed for reference)`

**Acceptance Criteria:**
- [ ] README has plugin explanation
- [ ] `.github/ISSUE_TEMPLATE/config.yml` exists
- [ ] CLAUDE.md docs/plans/ comment updated

**Commit:** `docs: enhance README, add issue config, clarify plans policy`

---

### T6: CI validation workflow [LOW]

**Why:** No automated validation exists. A simple GitHub Actions workflow catches issues early.

**File:** `.github/workflows/validate.yml`

**Checks:**
1. **JSON validation** — `jq . plugin.json` and `jq . marketplace.json`
2. **SKILL.md description length** — extract frontmatter, check <= 120 chars
3. **Markdown link checking** — verify internal cross-references resolve

**Approach:**
- Single workflow on push/PR to main
- `ubuntu-latest` runner
- Shell-only (jq, grep, awk) — no npm dependencies, matching config-only repo philosophy

**Acceptance Criteria:**
- [ ] Workflow file exists
- [ ] Validates JSON syntax
- [ ] Checks SKILL.md description length
- [ ] Passes on current repo state

**Commit:** `chore: add CI validation workflow for plugin manifests`

---

### T7: blog-digest E2E test [HIGH — Post-Push, Separate Session]

**Why:** Plan Task 8 (E2E validation) was never executed. The plugin has never been tested with a real blog URL.

**Execution context:** This task CANNOT be done in the current implementation session. It requires:
1. Push all commits to origin (`git push origin main`)
2. In a NEW Claude Code session:
   - `claude plugin marketplace add kim-jeonghyun/jh-claude-plugins`
   - `claude plugin install blog-digest@jh-claude-plugins`
   - Trigger: `블로그 정리 [stable public blog URL]`
3. Verify output contains: summary, key points, quiz sections
4. Document any issues as GitHub issues

**This task is excluded from the automated task flow.** It is a manual post-push verification step.

**Acceptance Criteria:**
- [ ] blog-digest skill executed against at least one real blog URL
- [ ] Output contains expected sections (summary, key points, quiz)
- [ ] Issues logged if found

---

## Git Strategy

**Total commits: 5** (T7 produces no commit unless fixes needed)

| Order | Commit | Files | Phase |
|-------|--------|-------|-------|
| 1 | `docs: replace CoC with full Contributor Covenant v2.1 text` | `CODE_OF_CONDUCT.md` | 1 |
| 2 | `fix(blog-digest): shorten SKILL.md description to under 120 chars` | `SKILL.md` | 1 |
| 3 | `docs: clean hardcoded paths and commit plan docs` | `docs/plans/*.md` (7 files) | 2 |
| 4 | `docs: enhance README, add issue config, clarify plans policy` | `README.md`, `config.yml`, `CLAUDE.md` | 3 |
| 5 | `chore: add CI validation workflow` | `validate.yml` | 3 |

## Verification Steps

After all commits:
1. `git log --oneline -7` — verify commit messages follow conventional format
2. `grep -r "<repo-root>" docs/plans/` — verify zero hardcoded paths
3. `wc -l CODE_OF_CONDUCT.md` — verify > 50 lines (full CC text)
4. `echo -n "$(sed -n 's/^description: //p' plugins/blog-digest/skills/blog-digest/SKILL.md)" | wc -m` — verify < 120 chars
5. `jq . .claude-plugin/marketplace.json && jq . plugins/blog-digest/.claude-plugin/plugin.json` — verify valid JSON
6. `git status` — verify clean working tree
7. Post-push: check `https://github.com/kim-jeonghyun/jh-claude-plugins/community` for CoC detection

## Deferred Items

- **Additional badges** (review item #9): Purely cosmetic, deferred to future session
- **E2E test execution** (T7): Requires separate session post-push

## Success Criteria

- All 3 HIGH items resolved (CoC full text, SKILL.md description, E2E test deferred with clear plan)
- All 2 MEDIUM items resolved (plan docs committed, hardcoded paths removed)
- All 4 LOW items resolved (CI, README, issue template, docs policy)
- Clean `git status`
- CI workflow passes on push
