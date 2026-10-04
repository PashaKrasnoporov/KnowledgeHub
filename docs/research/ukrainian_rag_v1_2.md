# KnowledgeHub RAG v1.2 — Ukrainian-first

## Goal

The primary generation mode is Ukrainian.

KnowledgeHub should be able to use Ukrainian, English or mixed-language
source documents while producing a Ukrainian answer by default.

## Language pipeline

```text
retrieved evidence
  -> Ukrainian-first prompt
  -> local LLM
  -> language-quality check
  -> optional Ukrainian rewrite pass
  -> claim-level grounding
  -> automatic citations
```

The rewrite pass is triggered only when the generated draft contains
clear Russian-language markers. It must preserve facts and cannot add
new information.

## Evidence gate

Before local generation, KnowledgeHub calculates evidence confidence
from the strongest retrieved chunks.

```text
0.70 * top chunk score
+ 0.30 * mean(top 3 chunk scores)
```

If confidence is below `0.30`, generation is not started. The system
returns a transparent insufficient-evidence message instead of forcing
the model to answer.

## UX

RAG v1.2 adds:

- Ukrainian as the default response language;
- optional automatic language mode;
- inline generation spinner;
- indeterminate progress bar;
- elapsed-time indicator;
- explicit notice that the bar is not a fake percentage;
- Ctrl+Enter submission;
- question character counter;
- copy-answer action;
- clickable citations;
- collapsed claim-audit section;
- evidence-confidence indicator.

## Research direction

This creates measurable dimensions for future evaluation:

- Ukrainian language quality;
- retrieval confidence;
- grounding coverage;
- unsupported-claim removal;
- fallback rate;
- response latency.
