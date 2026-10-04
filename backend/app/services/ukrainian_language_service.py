import re
from dataclasses import dataclass

from wordfreq import (
    zipf_frequency,
)


RUSSIAN_UNIQUE_LETTERS = re.compile(
    r"[ыЫэЭёЁъЪ]"
)

CYRILLIC_WORD_PATTERN = re.compile(
    r"[А-Яа-яІіЇїЄєҐґ'-]+"
)

LATIN_PATTERN = re.compile(
    r"[A-Za-z]"
)

RUSSIAN_MARKERS = {
    "является",
    "являются",
    "который",
    "которая",
    "которые",
    "которое",
    "служит",
    "служат",
    "используется",
    "используются",
    "позволяет",
    "позволяют",
    "обеспечивает",
    "обеспечивают",
    "контекста",
    "документа",
    "документов",
    "данные",
    "ответ",
    "источник",
    "источники",
    "информация",
    "поиск",
    "разбиение",
    "сохранение",
    "векторной",
    "векторных",
}

UNNATURAL_PATTERNS = {
    "пошукуван": "неприродна форма слова «пошук»",
    "семана-": "штучна форма «семана-»",
    "семантос": "штучна форма «семантос»",
    "лексичне метод": "порушення узгодження «лексичне метод»",
    "лексичні методі": "порушення узгодження «лексичні методі»",
    "контекста": "росіянізм «контекста»",
    "розуміння контекста": "російська калька",
    "віддіювання": "неприродна словоформа",
}

TECHNICAL_WHITELIST = {
    "алгоритм",
    "алгоритми",
    "вектор",
    "вектори",
    "векторний",
    "векторна",
    "векторне",
    "гібридний",
    "гібридна",
    "гібридне",
    "лексичний",
    "лексична",
    "лексичне",
    "релевантний",
    "релевантна",
    "релевантне",
    "семантичний",
    "семантична",
    "семантичне",
    "токен",
    "токени",
    "фрагмент",
    "фрагменти",
    "лематизація",
    "лематизації",
}

MIN_WORD_LENGTH_FOR_FREQUENCY = 5
UNKNOWN_WORD_LIMIT = 2


@dataclass
class UkrainianQualityResult:
    passed: bool
    issues: list[str]
    suspicious_words: list[str]


def _normalized_words(
    text: str,
) -> list[str]:
    return [
        word.lower().strip(
            "'-"
        )
        for word
        in CYRILLIC_WORD_PATTERN.findall(
            text
        )
        if word.strip(
            "'-"
        )
    ]


def _source_vocabulary(
    source_texts: list[str] | None,
) -> set[str]:
    if not source_texts:
        return set()

    vocabulary = set()

    for text in source_texts:
        vocabulary.update(
            _normalized_words(
                text
            )
        )

    return vocabulary


def _find_suspicious_words(
    text: str,
    source_texts: list[str] | None,
) -> list[str]:
    source_words = _source_vocabulary(
        source_texts
    )

    suspicious = []

    for word in _normalized_words(
        text
    ):
        if (
            len(word)
            < MIN_WORD_LENGTH_FOR_FREQUENCY
        ):
            continue

        if word in TECHNICAL_WHITELIST:
            continue

        if word in source_words:
            continue

        if LATIN_PATTERN.search(
            word
        ):
            continue

        frequency = zipf_frequency(
            word,
            "uk",
            wordlist="best",
        )

        if frequency <= 0.0:
            suspicious.append(
                word
            )

    return sorted(
        set(
            suspicious
        )
    )


def evaluate_ukrainian_quality(
    text: str,
    source_texts: list[str] | None = None,
) -> UkrainianQualityResult:
    issues = []

    if RUSSIAN_UNIQUE_LETTERS.search(
        text
    ):
        issues.append(
            "наявні російські літери"
        )

    words = _normalized_words(
        text
    )

    marker_hits = sorted({
        word
        for word in words
        if word in RUSSIAN_MARKERS
    })

    if marker_hits:
        issues.append(
            (
                "російські мовні форми: "
                + ", ".join(
                    marker_hits[:5]
                )
            )
        )

    lowered = text.lower()

    for (
        pattern,
        description,
    ) in UNNATURAL_PATTERNS.items():
        if pattern in lowered:
            issues.append(
                description
            )

    suspicious_words = (
        _find_suspicious_words(
            text=text,
            source_texts=source_texts,
        )
    )

    if (
        len(suspicious_words)
        >= UNKNOWN_WORD_LIMIT
    ):
        issues.append(
            (
                "підозрілі або вигадані словоформи: "
                + ", ".join(
                    suspicious_words[:6]
                )
            )
        )

    return UkrainianQualityResult(
        passed=not issues,
        issues=issues,
        suspicious_words=(
            suspicious_words
        ),
    )


def build_ukrainian_rewrite_messages(
    draft: str,
    strict: bool = False,
    issues: list[str] | None = None,
) -> list[dict[str, str]]:
    issue_text = ""

    if issues:
        issue_text = (
            "\n\nАвтоматична перевірка виявила:\n- "
            + "\n- ".join(
                issues
            )
        )

    strict_rules = ""

    if strict:
        strict_rules = """
Додатковий строгий контроль:
- не використовуй «пошукування», «семана-»,
  «семантос», «віддіювання»;
- пиши «семантичний пошук»;
- пиши «лексичний пошук» або «лексичний метод»;
- перевір узгодження роду, числа та відмінка;
- не утворюй нові слова, якщо можна використати
  звичайний український термін;
- якщо речення звучить як машинний переклад,
  перебудуй його простіше.
""".strip()

    system = f"""
Ти — професійний редактор українського
науково-технічного тексту.

Перепиши чернетку природною нормативною українською.

Обов'язково:
1. Не додавай нових фактів.
2. Не прибирай змістовних фактів.
3. Не змінюй причинно-наслідковий зміст.
4. Не використовуй російські слова або кальки.
5. Не вигадуй нових термінів чи словоформ.
6. Використовуй усталені формулювання:
   «семантичний пошук»,
   «лексичний пошук»,
   «векторне представлення»,
   «релевантний документ»,
   «змістова близькість».
7. Англійські терміни RAG, LLM, embeddings,
   retrieval, BM25 можна залишати англійською.
8. Не додавай citations, [1], [2] або номери джерел.
9. Поверни лише відредагований текст.

{strict_rules}
{issue_text}
""".strip()

    return [
        {
            "role": "system",
            "content": system,
        },
        {
            "role": "user",
            "content": draft,
        },
    ]
