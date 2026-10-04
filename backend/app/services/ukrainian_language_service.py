import re


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


def ukrainian_language_issues(
    text: str,
) -> list[str]:
    issues = []

    if RUSSIAN_UNIQUE_LETTERS.search(
        text
    ):
        issues.append(
            "російські літери"
        )

    words = [
        word.lower()
        for word
        in WORD_PATTERN.findall(
            text
        )
    ]

    marker_hits = [
        word
        for word in words
        if word in RUSSIAN_MARKERS
    ]

    if len(marker_hits) >= 2:
        issues.append(
            "російські мовні форми"
        )

    return issues


def needs_ukrainian_rewrite(
    text: str,
) -> bool:
    return bool(
        ukrainian_language_issues(
            text
        )
    )


def build_ukrainian_rewrite_messages(
    draft: str,
) -> list[dict[str, str]]:
    system = """
Ти — редактор українського технічного тексту.

Перепиши наданий текст нормативною українською мовою.

Обов'язкові правила:
1. Не додавай нових фактів.
2. Не прибирай факти з початкового тексту.
3. Не використовуй російські слова або граматичні конструкції.
4. Англійські технічні терміни embeddings, RAG, LLM,
   retrieval та назви моделей можна залишати англійською.
5. Не додавай citations, квадратні дужки або номери джерел.
6. Поверни лише виправлений текст без пояснень.
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
