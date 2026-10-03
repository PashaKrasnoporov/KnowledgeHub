import math

from app.baza_danykh.sesii import (
    FabrykaSesii,
)
from app.modeli.collection import Collection
from app.modeli.document import Document
from app.modeli.user import User
from app.services.document_service import (
    search_collection_documents,
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


def precision_at_k(
    ranked_names: list[str],
    relevant_names: set[str],
    k: int,
) -> float:
    top_k = ranked_names[:k]

    if not top_k:
        return 0.0

    relevant_count = sum(
        1
        for name in top_k
        if name in relevant_names
    )

    return relevant_count / k


def recall_at_k(
    ranked_names: list[str],
    relevant_names: set[str],
    k: int,
) -> float:
    if not relevant_names:
        return 0.0

    top_k = ranked_names[:k]

    relevant_count = sum(
        1
        for name in top_k
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
            return 1.0 / position

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
        relevance = (
            1.0
            if name in relevant_names
            else 0.0
        )

        if relevance:
            dcg += (
                relevance
                / math.log2(
                    position + 1
                )
            )

    ideal_relevant_count = min(
        len(relevant_names),
        k,
    )

    if ideal_relevant_count == 0:
        return 0.0

    idcg = sum(
        1.0
        / math.log2(
            position + 1
        )
        for position in range(
            1,
            ideal_relevant_count + 1,
        )
    )

    return dcg / idcg


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

        precision_values: list[float] = []
        recall_values: list[float] = []
        rr_values: list[float] = []
        ndcg_values: list[float] = []

        print(
            "\nLEXICAL BASELINE EVALUATION"
        )

        print(
            "=" * 60
        )

        for (
            query,
            relevant_names,
        ) in TEST_QUERIES.items():

            results = (
                search_collection_documents(
                    session=session,
                    collection=collection,
                    search_text=query,
                )
            )

            ranked_names = [
                result.document.original_name
                for result in results
            ]

            precision = precision_at_k(
                ranked_names,
                relevant_names,
                K,
            )

            recall = recall_at_k(
                ranked_names,
                relevant_names,
                K,
            )

            rr = reciprocal_rank(
                ranked_names,
                relevant_names,
            )

            ndcg = ndcg_at_k(
                ranked_names,
                relevant_names,
                K,
            )

            precision_values.append(
                precision
            )

            recall_values.append(
                recall
            )

            rr_values.append(
                rr
            )

            ndcg_values.append(
                ndcg
            )

            print(
                f"\nQuery: {query}"
            )

            if ranked_names:
                for index, result in enumerate(
                    results,
                    start=1,
                ):
                    print(
                        f"  {index}. "
                        f"{result.document.original_name}"
                        f" | score="
                        f"{result.score:.6f}"
                    )
            else:
                print(
                    "  Нічого не знайдено."
                )

            print(
                f"  Precision@{K}: "
                f"{precision:.3f}"
            )

            print(
                f"  Recall@{K}: "
                f"{recall:.3f}"
            )

            print(
                f"  RR: {rr:.3f}"
            )

            print(
                f"  nDCG@{K}: "
                f"{ndcg:.3f}"
            )

        query_count = len(
            TEST_QUERIES
        )

        mean_precision = (
            sum(precision_values)
            / query_count
        )

        mean_recall = (
            sum(recall_values)
            / query_count
        )

        mrr = (
            sum(rr_values)
            / query_count
        )

        mean_ndcg = (
            sum(ndcg_values)
            / query_count
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            "SUMMARY"
        )

        print(
            f"Mean Precision@{K}: "
            f"{mean_precision:.3f}"
        )

        print(
            f"Mean Recall@{K}: "
            f"{mean_recall:.3f}"
        )

        print(
            f"MRR: {mrr:.3f}"
        )

        print(
            f"Mean nDCG@{K}: "
            f"{mean_ndcg:.3f}"
        )

    finally:
        session.close()


if __name__ == "__main__":
    main()