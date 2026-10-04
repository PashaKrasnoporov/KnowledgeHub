# KnowledgeHub RAG v1.5.2

## Main changes

RAG v1.5 fixes two weaknesses found during practical Ukrainian testing:

1. `wordfreq` was too strict when used as a hard dictionary gate;
2. the old fallback could expose noisy test metadata or weak sentences.

## Ukrainian quality model

`wordfreq` is now a soft corpus signal.

A word missing from the corpus no longer automatically invalidates the answer.

### Hard failures

The answer is still rejected for:

- explicit Russian-only letters;
- known Russian forms;
- known artificial constructions;
- suspicious malformed technical compounds;
- language quality below the final threshold after two editorial passes.

### Soft warnings

Rare or corpus-unknown words:

- reduce the Ukrainian quality score;
- trigger a second editorial pass;
- are shown in the language audit;
- do not automatically reject otherwise valid Ukrainian text.

## Quality score

The score starts from `100`.

Critical language problems have a strong penalty.
Unknown corpus words have only a small penalty.

The final Ukrainian answer is accepted when:

- no critical issue remains;
- score is at least `78/100`.

## Editorial generation

The initial answer remains generative.

Ukrainian editorial passes are deterministic (`do_sample=False`) so
the proofreading stage is less likely to invent additional wording.

## Source-preserving fallback

The fallback never rewrites stored documents.

Instead it:

1. splits retrieved excerpts into sentences;
2. removes display-only list numbering;
3. truncates appended metadata such as `Код документа:` and `Ключові слова:`;
4. excludes obvious fixture/header noise;
5. scores remaining sentences against the question;
6. shows only the best source sentences with citations.

The actual PDF/DOCX/TXT text stored by KnowledgeHub is untouched.

## UI

The UI now shows:

- `RAG v1.5`;
- Ukrainian quality score `/100`;
- separate critical issues and warnings;
- a clear `Перевірений витяг із джерел` fallback label;
- an explanation that fallback does not modify the source files.

## v1.5.1 correction

- fixed PowerShell self-test quoting;
- `wordfreq` is now strictly a soft signal and cannot reject a response by itself;
- `wordfreq` is imported lazily;
- clean extractive fallback accepts concise valid sentences with six informative tokens;
- failed installer runs clean their own known untracked files.

## v1.5.2 delivery hardening

The installer no longer executes multiline Ukrainian Python code through
`python -c` in Windows PowerShell.

Smoke tests live in `backend/tests/test_rag_quality_smoke.py` and are
executed as a normal UTF-8 Python file. This avoids shell-quoting corruption
of Cyrillic test strings and makes the checks reusable later.
