import re
from dataclasses import dataclass

RUSSIAN_UNIQUE_LETTERS = re.compile(
    r"[ыЫэЭёЁъЪ]"
)

CYRILLIC_WORD_PATTERN = re.compile(
    r"[А-Яа-яІіЇїЄєҐґ'-]+"
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

CRITICAL_UNNATURAL_PATTERNS = {
    "пошукуван": "неприродна словоформа на основі «пошук»",
    "семана-": "штучна форма «семана-»",
    "семантос": "штучна форма «семантос»",
    "віддіювання": "неприродна словоформа «віддіювання»",
    "лексичне метод": "порушення узгодження «лексичне метод»",
    "лексичні методі": "порушення узгодження «лексичні методі»",
    "контекста": "росіянізм «контекста»",
    "розуміння контекста": "російська калька",
}

SUSPICIOUS_TECH_PATTERN = re.compile(
    r"\b(?:"
    r"семан[а-яіїєґ'-]*(?:вектор|лекс)"
    r"|лекс[а-яіїєґ'-]*семан"
    r"|пошукуван[а-яіїєґ'-]*"
    r"|віддіюван[а-яіїєґ'-]*"
    r")\b",
    flags=re.IGNORECASE,
)

TECHNICAL_PREFIXES = (
    "алгоритм",
    "вектор",
    "гібрид",
    "індекс",
    "лексич",
    "лемат",
    "релевант",
    "семантич",
    "токен",
    "фрагмент",
    "ембед",
)

MIN_WORD_LENGTH_FOR_FREQUENCY = 5
@dataclass
class UkrainianQualityResult:
    passed: bool
    score: int
    hard_issues: list[str]
    warnings: list[str]
    suspicious_words: list[str]
    needs_rewrite: bool


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


def _is_known_technical_word(
    word: str,
) -> bool:
    return any(
        word.startswith(
            prefix
        )
        for prefix
        in TECHNICAL_PREFIXES
    )


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

        if word in source_words:
            continue

        if _is_known_technical_word(
            word
        ):
            continue

        # Lazy import keeps ordinary FastAPI startup lighter.
        from wordfreq import zipf_frequency

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
    hard_issues = []
    warnings = []

    if RUSSIAN_UNIQUE_LETTERS.search(
        text
    ):
        hard_issues.append(
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
        hard_issues.append(
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
    ) in CRITICAL_UNNATURAL_PATTERNS.items():
        if pattern in lowered:
            hard_issues.append(
                description
            )

    suspicious_compounds = sorted(
        set(
            SUSPICIOUS_TECH_PATTERN.findall(
                text
            )
        )
    )

    if suspicious_compounds:
        hard_issues.append(
            "штучні технічні словоформи"
        )

    suspicious_words = (
        _find_suspicious_words(
            text=text,
            source_texts=source_texts,
        )
    )

    if suspicious_words:
        warnings.append(
            (
                "рідкісні або невідомі словоформи: "
                + ", ".join(
                    suspicious_words[:6]
                )
            )
        )

    score = 100

    score -= min(
        70,
        28 * len(
            hard_issues
        ),
    )

    score -= min(
        24,
        6 * len(
            suspicious_words
        ),
    )

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    # wordfreq is only a soft signal. Unknown corpus words
    # can trigger proofreading and lower the score, but only
    # critical language errors can reject the final answer.
    passed = not hard_issues

    needs_rewrite = (
        bool(
            hard_issues
        )
        or len(
            suspicious_words
        ) >= 1
        or score < 90
    )

    return UkrainianQualityResult(
        passed=passed,
        score=score,
        hard_issues=hard_issues,
        warnings=warnings,
        suspicious_words=(
            suspicious_words
        ),
        needs_rewrite=(
            needs_rewrite
        ),
    )


def build_ukrainian_rewrite_messages(
    draft: str,
    strict: bool = False,
    issues: list[str] | None = None,
    warnings: list[str] | None = None,
) -> list[dict[str, str]]:
    diagnostics = []

    if issues:
        diagnostics.extend(
            issues
        )

    if warnings:
        diagnostics.extend(
            warnings
        )

    diagnostics_text = ""

    if diagnostics:
        diagnostics_text = (
            "\n\nАвтоматична перевірка виявила:\n- "
            + "\n- ".join(
                diagnostics
            )
        )

    strict_rules = ""

    if strict:
        strict_rules = """
Додатковий строгий контроль:
- не використовуй «пошукування», «семана-»,
  «семантос», «віддіювання»;
- не створюй нові складені терміни через дефіс,
  якщо такого терміна немає у вихідній чернетці;
- пиши «семантичний пошук»;
- пиши «лексичний пошук» або «лексичний метод»;
- перевір узгодження роду, числа та відмінка;
- якщо слово виглядає штучно, заміни його
  звичайним усталеним українським словом;
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
{diagnostics_text}
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
