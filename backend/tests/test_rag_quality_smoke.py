from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.extractive_fallback_service import prepare_source_sentence
from app.services.ukrainian_language_service import evaluate_ukrainian_quality


def test_ukrainian_quality():
    bad = evaluate_ukrainian_quality(
        "Семантос-векторне пошукування використовується для контекста."
    )
    assert not bad.passed
    assert bad.hard_issues

    good = evaluate_ukrainian_quality(
        "Семантичний пошук знаходить релевантні фрагменти за змістовою близькістю."
    )
    assert good.passed
    print("UA quality self-test: OK", f"score={good.score}")


def test_fallback_cleanup():
    source = (
        "Семантичний пошук порівнює зміст запиту з документами. "
        "Код документа: KH-TEST-02 Ключові слова: search"
    )
    result = prepare_source_sentence(source)
    expected = "Семантичний пошук порівнює зміст запиту з документами."
    assert result == expected, f"Unexpected fallback cleanup: {result!r}"
    print("Fallback cleanup self-test: OK")


def main():
    test_ukrainian_quality()
    test_fallback_cleanup()
    print("ALL RAG SMOKE TESTS: OK")


if __name__ == "__main__":
    main()
