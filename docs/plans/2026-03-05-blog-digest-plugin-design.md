# Blog Digest Plugin Design

Date: 2026-03-05
Status: Approved

## Overview

YouTube digest plugin과 동일한 학습+퀴즈 패턴을 블로그 콘텐츠에 적용하는 Claude Code 플러그인.

## Repository

- **Name**: `kim-jeonghyun/jh-claude-plugins`
- **Type**: Public monorepo (Claude Code plugins)
- **First plugin**: `blog-digest`

## File Structure

```
jh-claude-plugins/
├── plugins/
│   └── blog-digest/
│       ├── .claude-plugin/plugin.json
│       ├── skills/blog-digest/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── quiz-patterns.md
│       │       └── deep-research.md
│       └── README.md
└── README.md
```

## Workflow (7 Steps)

### 1. Content Extraction
- Tool: WebFetch
- Input: Blog URL
- Output: HTML content (title, author, date, body)

### 2. Metadata Parsing
- OG tags, meta tags에서 추출: title, author, date, description
- WebFetch 결과에서 직접 파싱 (외부 스크립트 불필요)

### 3. Context Gathering
- Tool: WebSearch
- 고유명사, 전문용어 맥락 파악
- Queries: "{제목} {저자} summary", "{핵심 키워드} 분석"

### 4. Document Generation

```markdown
---
title: {블로그 제목}
url: {Blog URL}
author: {저자}
source: {사이트명}
date: {게시 날짜}
processed_at: {처리 일시}
type: blog
---

# {블로그 제목}

## Summary
{3-5문장 요약 + 주요 포인트 3개}

## Insights
### Core Ideas
### Applicable Points
### Turtle Trading System Connections

## Full Text (Korean)
{한글 블로그: 원문 정리 / 영문 블로그: 한글 번역}
```

### 5. File Save
- Path: `/Users/momo/Library/Mobile Documents/iCloud~md~obsidian/Documents/test/02_Area/01_투자/blog/{category}/`
- Filename: `YYYY-MM-DD-{sanitized-title}.md`
- Categories (YouTube digest와 동일):
  - `chart_analysis/` - 차트 기술적 분석
  - `risk_management/` - 리스크 관리, 자금 관리
  - `macro/` - 거시 경제, 금리, 환율
  - `value_investing/` - 가치 투자, 기업 분석
  - `trading_psychology/` - 매매 심리, 멘탈 관리
  - `strategy/` - 매매 전략, 시스템 트레이딩, 백테스트

### 6. Quiz
- 3 levels x 3 questions = 9 questions total
- Same pattern as YouTube digest (references/quiz-patterns.md)
- AskUserQuestion으로 단계별 출제

### 7. Follow-up
- Re-quiz with different questions
- Deep Research (web deep-dive)
- Done

## Key Differences from YouTube Digest

| Aspect | YouTube | Blog |
|--------|---------|------|
| Content extraction | yt-dlp scripts | WebFetch (built-in) |
| Metadata | yt-dlp --dump-json | HTML meta/OG tags |
| Transcript correction | Required (auto-caption errors) | Not needed |
| Translation | Always translate to Korean | Korean: keep original, English: translate |
| External dependencies | yt-dlp CLI required | None |

## Future Expansion

- Codex / OpenClaw adapters (separate platform wrappers)
- Podcast digest plugin (same monorepo)
- RSS feed batch processing
