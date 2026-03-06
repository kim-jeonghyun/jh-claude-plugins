# Quiz Patterns

3-level quiz guide for blog digest comprehension testing.

## Question Types by Level

### Level 1 (Basic) - Insight Comprehension

Verify understanding of core message and key concepts:
- "What is the core message of this article?"
- "What principle did the author emphasize most?"
- "What main problem does the article identify?"

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
   - Why it is correct (reference article content)
   - Relevant section of the article
