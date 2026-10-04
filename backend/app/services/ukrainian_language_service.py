import re
from dataclasses import dataclass


RUSSIAN_UNIQUE_LETTERS = re.compile(
    r"[ыЫэЭёЁъЪ]"
)

WORD_PATTERN = re.compile(
    r"[A-Za-zА-Яа-яІіЇїЄєҐґ'-]+"
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
    "векторній базі": "сумнівна калькована конструкція",
    "віддіювання": "неприродна словоформа",
}


@dataclass
class UkrainianQualityResult:
    passed: bool
    issues: list[str]


def ukrainian_language_issues(
    text: str,
) -> list[str]:
    issues = []

    if RUSSIAN_UNIQUE_LETTERS.search(
        text
    ):
        issues.append(
            "наявні російські літери"
        )

    words = [
        word.lower()
        for word
        in WORD_PATTERN.findall(
            text
        )
    ]

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

    return issues


def evaluate_ukrainian_quality(
    text: str,
) -> UkrainianQualityResult:
    issues = ukrainian_language_issues(
        text
    )

    return UkrainianQualityResult(
        passed=not issues,
        issues=issues,
    )


def build_ukrainian_rewrite_messages(
    draft: str,
    strict: bool = False,
) -> list[dict[str, str]]:
    strict_rules = ""

    if strict:
        strict_rules = """
Додатковий строгий контроль:
- не використовуй слова «пошукування», «семана-»,
  «семантос», «віддіювання»;
- пиши «семантичний пошук», а не штучні похідні;
- пиши «лексичний пошук» або «лексичний метод»;
- перевір узгодження роду, числа та відмінка;
- якщо речення звучить як машинний переклад,
  перебудуй його простіше;
- краще два простих природних речення,
  ніж одне складне кальковане.
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
