import math

from app.baza_danykh.sesii import (
    FabrykaSesii,
)
from app.modeli.collection import Collection
from app.services.hybrid_search_service import (
    search_hybrid_documents,
)


COLLECTION_ID = 1

K = 3


TEST_QUERIES = {
    "BM25": {
        "01_lexical_search_bm25.txt",
        "03_hybrid_retrieval.pdf",
    },

    "embeddings": {
        "02_semantic_embeddings.docx",
        "03_hybrid_retrieval.pdf",
        "04_rag_pipeline.docx",
    },

    "RAG": {
        "04_rag_pipeline.docx",
    },

    "lexical search": {
        "01_lexical_search_bm25.txt",
        "03_hybrid_retrieval.pdf",
    },

    "Precision Recall MRR nDCG": {
        "05_retrieval_evaluation.pdf",
    },
}


WEIGHT_VARIANTS = [
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
]


def precision_at_k(
    ranked_names: list[str],
    relevant_names: set[str],
    k: int,
) -> float:
    relevant_count = sum(
        1
        for name in ranked_names[:k]
        if name in relevant_names
    )

    return (
        relevant_count
        / k
    )


def recall_at_k(
    ranked_names: list[str],
    relevant_names: set[str],
    k: int,
) -> float:
    if not relevant_names:
        return 0.0

    relevant_count = sum(
        1
        for name in ranked_names[:k]
        if name in relevant_names
    )

    return (
        relevant_count
        / len(relevant_names)
    )


def reciprocal_rank(
    ranked_names: list[str],
    relevant_names: set[str],
) -> float:
    for position, name in enumerate(
        ranked_names,
        start=1,
    ):
        if name in relevant_names:
            return (
                1.0
                / position
            )

    return 0.0


def ndcg_at_k(
    ranked_names: list[str],
    relevant_names: set[str],
    k: int,
) -> float:
    dcg = 0.0

    for position, name in enumerate(
        ranked_names[:k],
        start=1,
    ):
        if name in relevant_names:
            dcg += (
                1.0
                / math.log2(
                    position + 1
                )
            )

    ideal_count = min(
        len(relevant_names),
        k,
    )

    if ideal_count == 0:
        return 0.0

    idcg = sum(
        1.0
        / math.log2(
            position + 1
        )
        for position in range(
            1,
            ideal_count + 1,
        )
    )

    return (
        dcg
        / idcg
    )


def evaluate_weights(
    session,
    collection,
    lexical_weight: float,
) -> dict[str, float]:
    semantic_weight = (
        1.0
        - lexical_weight
    )

    precision_values: list[float] = []
    recall_values: list[float] = []
    rr_values: list[float] = []
    ndcg_values: list[float] = []

    for (
        query,
        relevant_names,
    ) in TEST_QUERIES.items():

        results = (
            search_hybrid_documents(
                session=session,
                collection=collection,
                search_text=query,
                lexical_weight=(
                    lexical_weight
                ),
                semantic_weight=(
                    semantic_weight
                ),
                limit=10,
            )
        )

        ranked_names = [
            result.document.original_name
            for result in results
        ]

        precision_values.append(
            precision_at_k(
                ranked_names,
                relevant_names,
                K,
            )
        )

        recall_values.append(
            recall_at_k(
                ranked_names,
                relevant_names,
                K,
            )
        )

        rr_values.append(
            reciprocal_rank(
                ranked_names,
                relevant_names,
            )
        )

        ndcg_values.append(
            ndcg_at_k(
                ranked_names,
                relevant_names,
                K,
            )
        )

    count = len(
        TEST_QUERIES
    )

    return {
        "precision": (
            sum(precision_values)
            / count
        ),
        "recall": (
            sum(recall_values)
            / count
        ),
        "mrr": (
            sum(rr_values)
            / count
        ),
        "ndcg": (
            sum(ndcg_values)
            / count
        ),
    }


def main() -> None:
    session = FabrykaSesii()

    try:
        collection = session.get(
            Collection,
            COLLECTION_ID,
        )

        if collection is None:
            print(
                "Колекцію не знайдено."
            )
            return

        print(
            "\nHYBRID WEIGHT SEARCH"
        )

        print(
            "=" * 76
        )

        best_weight = None
        best_metrics = None
        best_score = -1.0

        for lexical_weight in (
            WEIGHT_VARIANTS
        ):
            semantic_weight = (
                1.0
                - lexical_weight
            )

            metrics = evaluate_weights(
                session=session,
                collection=collection,
                lexical_weight=(
                    lexical_weight
                ),
            )

            combined_score = (
                metrics["precision"]
                + metrics["recall"]
                + metrics["mrr"]
                + metrics["ndcg"]
            ) / 4.0

            print(
                f"Lexical={lexical_weight:.1f} "
                f"Semantic={semantic_weight:.1f}"
                f" | P@{K}="
                f"{metrics['precision']:.3f}"
                f" | R@{K}="
                f"{metrics['recall']:.3f}"
                f" | MRR="
                f"{metrics['mrr']:.3f}"
                f" | nDCG="
                f"{metrics['ndcg']:.3f}"
                f" | AVG="
                f"{combined_score:.3f}"
            )

            if combined_score > best_score:
                best_score = (
                    combined_score
                )

                best_weight = (
                    lexical_weight
                )

                best_metrics = (
                    metrics
                )

        if (
            best_weight is None
            or best_metrics is None
        ):
            return

        semantic_weight = (
            1.0
            - best_weight
        )

        print(
            "\n"
            + "=" * 76
        )

        print(
            "BEST CONFIGURATION"
        )

        print(
            f"Lexical weight: "
            f"{best_weight:.1f}"
        )

        print(
            f"Semantic weight: "
            f"{semantic_weight:.1f}"
        )

        print(
            f"Mean Precision@{K}: "
            f"{best_metrics['precision']:.3f}"
        )

        print(
            f"Mean Recall@{K}: "
            f"{best_metrics['recall']:.3f}"
        )

        print(
            f"MRR: "
            f"{best_metrics['mrr']:.3f}"
        )

        print(
            f"Mean nDCG@{K}: "
            f"{best_metrics['ndcg']:.3f}"
        )

        print(
            f"Average metric: "
            f"{best_score:.3f}"
        )

        print(
            "\nRANKING WITH BEST WEIGHTS"
        )

        print(
            "=" * 76
        )

        for (
            query,
            relevant_names,
        ) in TEST_QUERIES.items():

            results = (
                search_hybrid_documents(
                    session=session,
                    collection=collection,
                    search_text=query,
                    lexical_weight=(
                        best_weight
                    ),
                    semantic_weight=(
                        semantic_weight
                    ),
                    limit=10,
                )
            )

            print(
                f"\nQuery: {query}"
            )

            for index, result in enumerate(
                results,
                start=1,
            ):
                marker = (
                    "*"
                    if (
                        result.document.original_name
                        in relevant_names
                    )
                    else " "
                )

                print(
                    f"{marker} {index}. "
                    f"{result.document.original_name}"
                    f" | hybrid="
                    f"{result.score:.6f}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()