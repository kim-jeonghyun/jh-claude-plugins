# Quiz Patterns

3-level quiz guide for video digest comprehension testing.

## Question Types by Level

### Level 1 (Basic) - Insight Comprehension

Verify understanding of core message and key concepts:
- "What is the core message of this video?"
- "What principle did the author emphasize most?"
- "What main problem does the video identify?"

### Level 2 (Intermediate) - Insight-Detail Connection

Verify relationships between concepts and supporting evidence:
- "What evidence did the author provide for concept X?"
- "What difference was explained between A and B?"
- "What advantage was mentioned for this approach?"

### Level 3 (Advanced) - Detail & Application

Case analysis and specific data:
- "What success factor was identified in the mentioned case?"
- "What caution was noted when applying this approach?"
- "What specific data/numbers did the author present?"

## AskUserQuestion Format

Use AskUserQuestion with up to 3 questions per call (one per quiz question in the level):

```
AskUserQuestion:
questions:
  - question: "[Level 1 - Basic] Question 1..."
    header: "Q1"
    options:
      - label: "A"
        description: "Option A description"
      - label: "B"
        description: "Option B description"
      - label: "C"
        description: "Option C description"
      - label: "D"
        description: "Option D description"
    multiSelect: false
  - question: "[Level 1 - Basic] Question 2..."
    header: "Q2"
    ...
  - question: "[Level 1 - Basic] Question 3..."
    header: "Q3"
    ...
```

## Result Processing

After each level:
1. Show correct/incorrect immediately
2. For wrong answers, provide detailed explanation:
   - What the correct answer is
   - Why it is correct (reference video content)
   - Relevant section of the video

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
