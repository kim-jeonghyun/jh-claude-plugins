# YouTube Digest v2 — Design Document

> **Date:** 2026-03-06
> **Status:** Approved
> **Approach:** Layered Enhancement (접근 A)
> **Target repo:** `<repo-root>/` (monorepo, blog-digest와 공존)

## Background

### Problem

team-attention-plugins의 youtube-digest (v0.2.0, MIT License)는 30분 이상 영상에서 요약 깊이가 현저히 떨어진다. 2시간 26분 영상을 "3-5문장 + 3포인트"로 요약하면 사용자로부터 "내용이 너무 짧다"는 피드백을 받는다.

### Root Causes

| # | 원인 | 영향 |
|---|------|------|
| 1 | 영상 길이 무관 단일 템플릿 | 긴 영상도 3-5문장으로 압축 |
| 2 | 긴 transcript 처리 전략 부재 | LLM이 전체를 뭉뚱그려 요약 |
| 3 | 토픽 세그멘테이션 미지원 | 주제별 분석 불가 |
| 4 | extract_transcript.sh 버그 | `--convert-subs json3` 무효 옵션 |
| 5 | 퀴즈 커버리지 불균형 | 9문제로 2시간 영상 검증 불가 |

### License

원본: MIT License (Copyright (c) 2025 Team Attention). Fork, 수정, 재배포 가능. 유일한 의무: 원본 저작권 고지 포함.

## Decision: Layered Enhancement

기존 8단계 워크플로우를 유지하면서 조건부 분기 로직을 추가한다.

**선택 이유:**
- 원본 구조를 존중하면서 개선점만 추가 (fork 취지)
- 짧은 영상에서 불필요한 복잡도 없음
- SKILL.md 하나에서 전체 흐름 파악 가능 (LLM 컨텍스트 효율적)

**기각된 접근:**
- Modular Rewrite (B): 파일 수 증가, LLM 컨텍스트 비용 증가
- Preset System (C): 프리셋 간 중복 코드, 공통 변경 시 3곳 수정

---

## Architecture

### Repository Structure

```
jh-claude-plugins/
├── .claude-plugin/marketplace.json     # youtube-digest 항목 추가
├── NOTICE                              # Team Attention attribution
├── shared/                             # 공유 references (신규)
│   ├── quiz-patterns.md                # 퀴즈 출제 가이드 + 스케일링
│   ├── deep-research.md                # Deep Research 워크플로우
│   ├── category-config.md              # 카테고리 분류 + 온보딩
│   └── output-save.md                  # 저장 대상 추상화 (Obsidian/Notion/로컬)
├── plugins/
│   ├── blog-digest/                    # 기존 (references → shared 참조로 전환)
│   └── youtube-digest/                 # 신규 (fork + 개선)
│       ├── .claude-plugin/plugin.json
│       ├── LICENSE.original            # Team Attention MIT 원본
│       ├── README.md
│       └── skills/youtube-digest/
│           ├── SKILL.md                # 개선된 메인 워크플로우
│           ├── scripts/
│           │   ├── extract_metadata.sh
│           │   └── extract_transcript.sh  # 버그 수정 (srt)
│           └── references/
│               └── templates/
│                   ├── short.md        # ~30분
│                   ├── medium.md       # 30분~2시간
│                   └── long.md         # 2시간+
```

### shared/ 모듈

blog-digest와 youtube-digest 간 공통 로직을 공유한다.

| 파일 | 역할 | 참조 원본 |
|------|------|----------|
| quiz-patterns.md | 퀴즈 출제 패턴 + 스케일링 규칙 | blog-digest 기존 것 이동 + 확장 |
| deep-research.md | Deep Research 워크플로우 | blog-digest 기존 것 이동 (변경 없음) |
| category-config.md | 카테고리 분류 + 온보딩 | MEMORY.md 기반 설정 |
| output-save.md | 저장 대상 추상화 | 신규 |

**output-save.md 저장 대상 분기:**

| 대상 | 설정 | 동작 |
|------|------|------|
| Obsidian | `save_path: ~/Library/.../vault/` | Write로 .md 직접 저장 |
| Notion | `save_target: notion` | 문서 생성 후 클립보드 복사 안내 |
| 로컬 파일 | `save_path: ./digests/` | 프로젝트 상대 경로 저장 |

설정 우선순위: MEMORY.md 존재 → 사용 / 없으면 → 첫 실행 시 AskUserQuestion으로 질문 후 MEMORY.md에 기록.

---

## Workflow Design

기존 8단계 + Step 1.5(전략 결정) + Step 2.5(2-pass 분석):

```
Step 1:   메타데이터 수집 (기존 유지)
Step 1.5: 영상 길이 판별 → 처리 전략 결정 (신규)
Step 2:   Transcript 추출 (스크립트 버그 수정)
Step 2.5: 토픽 세그멘테이션 — Pass 1 (신규, 30분+ only)
Step 3:   맥락 파악 — WebSearch (기존 유지)
Step 4:   Transcript 교정 (기존 유지)
Step 5:   문서 생성 — 적응형 템플릿 (대폭 개선)
Step 6:   파일 저장 — output-save.md 참조 (일반화)
Step 7:   학습 퀴즈 — 스케일링 적용 (개선)
Step 8:   후속 선택 (기존 유지)
```

### Step 1.5: 처리 전략 결정

메타데이터의 duration 기반으로 preset 결정:

| Preset | Duration | 템플릿 | 전체 스크립트 | 퀴즈 |
|--------|----------|--------|-------------|------|
| SHORT  | ~30분    | short.md | 전체 번역 | 9문제 (3x3) |
| MEDIUM | 30분~2시간 | medium.md | 핵심 발언 발췌 | 9문제 (3x3) |
| LONG   | 2시간+   | long.md | 핵심 발언 발췌 | 12~15문제 (3~5 x 3) |

### Step 2.5: 2-Pass 분석 (MEDIUM/LONG only)

**Pass 1 — 목차 생성:**

전체 transcript를 청크 단위로 읽으면서:
1. 주제 전환점 식별 (화제 변경, "다음으로", 새 질문 등)
2. 각 토픽에 타임스탬프 + 제목 부여
3. 목차(Table of Contents) 생성

출력 예시:
```
Part 1 [00:00~15:30] 오프닝 & 시장 현황
Part 2 [15:30~35:20] 이란 전쟁 분석
Part 3 [35:20~55:00] 미국 섹터 로테이션
```

**Pass 2 — 파트별 상세 분석:**

각 파트의 transcript 구간을 집중 분석하여:
- 핵심 주장 + 근거 정리
- 구체적 수치/데이터 추출
- 인사이트 도출

SHORT preset은 이 단계를 건너뜀.

### Step 5: 적응형 템플릿

preset에 따라 `references/templates/{preset}.md` 참조:

**SHORT** (~30분):
```markdown
## 요약
{3-5문장 요약 + 주요 포인트 3개}

## 인사이트
### 핵심 아이디어
### 적용 가능한 점

## 전체 스크립트 (한글 번역)
[00:00] ...
```

**MEDIUM** (30분~2시간):
```markdown
## 요약
{5-8문장 요약 + 주요 포인트 5개}

## Part 1: {제목} [{시작}~{끝}]
### 핵심
### 세부 내용
### 인사이트

## Part N: ...

## 핵심 발언
| 시간 | 발언 |
|------|------|
| [MM:SS] | "인용문" |
```

**LONG** (2시간+):
```markdown
## 요약
{8-12문장 요약 + 주요 포인트 7개}

## Part 1: {제목} [{시작}~{끝}]
### 핵심
### 세부 내용
### 데이터/수치
### 인사이트

## Part N: ...

## 종합 분석
{파트 간 연결고리, 크로스레퍼런스}

## 핵심 발언
| 시간 | 발언 |
|------|------|
| [MM:SS] | "인용문" |
```

### Step 7: 퀴즈 스케일링

| Preset | 문제 수 | 구성 | AskUserQuestion 호출 |
|--------|--------|------|---------------------|
| SHORT  | 9문제  | 3단계 x 3문제 | 3회 (단계당 1회) |
| MEDIUM | 9문제  | 3단계 x 3문제 (파트 균등 배분) | 3회 |
| LONG   | 12~15문제 | 3단계 x 4~5문제 | 6회 (단계당 2회) |

LONG 퀴즈: AskUserQuestion 4문제 제한을 감안하여 단계당 2회 호출. 모든 파트에서 최소 1문제씩 출제하여 커버리지 보장.

---

## Bug Fix: extract_transcript.sh

```bash
# Before (broken)
yt-dlp --write-auto-sub --sub-lang "ko,en" --skip-download --convert-subs json3 \
  -o "$OUTPUT_DIR/%(title)s.%(ext)s" "$URL"

# After (fixed)
yt-dlp --write-auto-sub --sub-lang "ko,en" --sub-format srt --skip-download \
  -o "$OUTPUT_DIR/%(title)s.%(ext)s" "$URL"
```

`--convert-subs json3` → `--sub-format srt`. SRT가 가장 안정적이고 파싱이 간단.

---

## Error Handling

| 상황 | 대응 |
|------|------|
| 자막 없는 영상 | "자막을 추출할 수 없습니다" 안내 후 종료 |
| 자막 품질 매우 낮음 | `[불명확]` 마커 사용, 웹 검색으로 보완 |
| 라이브 진행 중 영상 | 메타데이터 `is_live` 확인 → 종료된 라이브만 처리 |
| yt-dlp 미설치 | `brew install yt-dlp` 안내 후 종료 |
| Transcript 컨텍스트 초과 | 청크 크기 조절 (기본 3000줄, 초과 시 2000줄로 재시도) |
| 저장 경로 접근 불가 | 에러 메시지 + 대체 경로 제안 |

---

## blog-digest 변경 사항

youtube-digest 추가 시 blog-digest에 필요한 최소 변경:

1. `references/quiz-patterns.md` → 삭제, `shared/quiz-patterns.md` 참조로 교체
2. `references/deep-research.md` → 삭제, `shared/deep-research.md` 참조로 교체
3. SKILL.md 내 경로 수정 (2곳)

로직 변경 없음. 경로만 수정.

---

## Attribution

```
NOTICE 파일:

youtube-digest is based on youtube-digest from team-attention-plugins.
Copyright (c) 2025 Team Attention
Licensed under the MIT License.
See plugins/youtube-digest/LICENSE.original for the full license text.
```
