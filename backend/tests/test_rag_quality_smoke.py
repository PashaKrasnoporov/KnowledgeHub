from pathlib import Path
import sys

import numpy as np

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_ROOT),
    )

from app.schemas.research import (
    ResearchResponseAPI,
    ResearchSourceAPI,
)
from app.services.extractive_fallback_service import (
    prepare_source_sentence,
)
from app.services.ukrainian_language_service import (
    evaluate_ukrainian_quality,
)
import app.services.claim_grounding_service as grounding_service


def test_ukrainian_quality():
    bad = evaluate_ukrainian_quality(
        "Семантос-векторне пошукування "
        "використовується для контекста."
    )

    assert not bad.passed
    assert bad.hard_issues

    v16_bad = evaluate_ukrainian_quality(
        "Семанто-векторне пошукування відряджується "
        "через зміжних форм і векторійності."
    )

    assert not v16_bad.passed
    assert v16_bad.hard_issues

    good = evaluate_ukrainian_quality(
        "Семантичний пошук знаходить "
        "релевантні фрагменти за "
        "змістовою близькістю."
    )

    assert good.passed

    print(
        "UA quality self-test: OK",
        f"score={good.score}",
    )


def test_fallback_cleanup():
    source = (
        "Семантичний пошук порівнює зміст "
        "запиту з документами. "
        "Код документа: KH-TEST-02 "
        "Ключові слова: search"
    )

    result = prepare_source_sentence(
        source
    )

    expected = (
        "Семантичний пошук порівнює "
        "зміст запиту з документами."
    )

    assert result == expected, (
        f"Unexpected fallback cleanup: {result!r}"
    )

    print(
        "Fallback cleanup self-test: OK"
    )


def test_internal_embeddings_are_not_serialized():
    source = ResearchSourceAPI(
        source_number=1,
        document_id=1,
        original_name="test.txt",
        chunk_index=0,
        excerpt="Семантичний пошук використовує embeddings.",
        score=0.8,
        semantic_score=0.8,
        lexical_score=0.6,
        embedding=[1.0, 0.0],
    )

    dumped = source.model_dump()

    assert "embedding" not in dumped

    print(
        "Internal embedding serialization: OK"
    )


def test_grounding_reuses_source_embeddings():
    research = ResearchResponseAPI(
        question="Що таке семантичний пошук?",
        mode="hybrid-chunks",
        count=1,
        answer_points=[],
        sources=[
            ResearchSourceAPI(
                source_number=1,
                document_id=1,
                original_name="test.txt",
                chunk_index=0,
                excerpt=(
                    "Семантичний пошук знаходить "
                    "релевантні документи за змістом."
                ),
                score=0.9,
                semantic_score=0.9,
                lexical_score=0.7,
                embedding=[1.0, 0.0],
            )
        ],
    )

    calls = []
    original = (
        grounding_service.create_text_embeddings
    )

    def fake_embeddings(texts):
        calls.append(
            list(texts)
        )

        return np.asarray(
            [
                [1.0, 0.0]
                for _text in texts
            ],
            dtype=np.float32,
        )

    grounding_service.create_text_embeddings = (
        fake_embeddings
    )

    try:
        result = (
            grounding_service.ground_generated_answer(
                generated_text=(
                    "Семантичний пошук знаходить "
                    "релевантні документи за змістом."
                ),
                research=research,
            )
        )
    finally:
        grounding_service.create_text_embeddings = (
            original
        )

    assert result.claims
    assert len(calls) == 1
    assert len(calls[0]) == 1

    print(
        "Stored source embedding reuse: OK"
    )


def main():
    test_ukrainian_quality()
    test_fallback_cleanup()
    test_internal_embeddings_are_not_serialized()
    test_grounding_reuses_source_embeddings()

    print(
        "ALL RAG SMOKE TESTS: OK"
    )


if __name__ == "__main__":
    main()
