<script setup>
import {
    computed
} from "vue"

const props = defineProps({
    documents: {
        type: Array,
        default: () => []
    }
})

const totalSize = computed(
    () =>
        props.documents.reduce(
            (sum, document) =>
                sum
                + Number(
                    document.size_bytes
                    || 0
                ),
            0
        )
)

const readyCount = computed(
    () =>
        props.documents.filter(
            document =>
                document.processing_status
                === "ready"
        ).length
)

const pendingCount = computed(
    () =>
        props.documents.filter(
            document => (
                document.processing_status === "pending"
                || document.processing_status === "processing"
            )
        ).length
)

const errorCount = computed(
    () =>
        props.documents.filter(
            document =>
                document.processing_status
                === "error"
        ).length
)

const formats = computed(
    () => {
        const values =
            props.documents.map(
                document => {
                    const name =
                        (
                            document.original_name
                            || ""
                        ).toLowerCase()

                    if (
                        name.endsWith(
                            ".pdf"
                        )
                    ) {
                        return "PDF"
                    }

                    if (
                        name.endsWith(
                            ".docx"
                        )
                    ) {
                        return "DOCX"
                    }

                    if (
                        name.endsWith(
                            ".txt"
                        )
                    ) {
                        return "TXT"
                    }

                    return "OTHER"
                }
            )

        return [
            ...new Set(values)
        ]
    }
)

function formatSize(
    bytes
) {
    const value =
        Number(bytes || 0)

    if (
        value < 1024
    ) {
        return (
            value
            + " Б"
        )
    }

    if (
        value < 1024 * 1024
    ) {
        return (
            (
                value / 1024
            ).toFixed(1)
            + " КБ"
        )
    }

    return (
        (
            value
            / 1024
            / 1024
        ).toFixed(2)
        + " МБ"
    )
}
</script>

<template>
    <section
        class="collection-overview"
        aria-label="Огляд колекції"
    >
        <div class="collection-overview-heading">
            <p class="eyebrow">
                OVERVIEW
            </p>

            <h2>
                Огляд колекції
            </h2>
        </div>

        <div class="collection-overview-grid">
            <article class="collection-overview-card">
                <span class="collection-overview-label">
                    Документи
                </span>

                <strong class="collection-overview-value">
                    {{ documents.length }}
                </strong>

                <span class="collection-overview-note">
                    усього в колекції
                </span>
            </article>

            <article class="collection-overview-card">
                <span class="collection-overview-label">
                    Загальний розмір
                </span>

                <strong class="collection-overview-value">
                    {{ formatSize(totalSize) }}
                </strong>

                <span class="collection-overview-note">
                    сумарний обсяг файлів
                </span>
            </article>

            <article class="collection-overview-card">
                <span class="collection-overview-label">
                    Обробка
                </span>

                <strong class="collection-overview-value">
                    {{ readyCount }}
                </strong>

                <span class="collection-overview-note">
                    готово
                    · {{ pendingCount }} в обробці
                    · {{ errorCount }} помилок
                </span>
            </article>

            <article class="collection-overview-card">
                <span class="collection-overview-label">
                    Формати
                </span>

                <strong
                    class="collection-overview-formats"
                >
                    {{
                        formats.length
                            ? formats.join(" · ")
                            : "—"
                    }}
                </strong>

                <span class="collection-overview-note">
                    доступні типи документів
                </span>
            </article>
        </div>
    </section>
</template>

<style scoped>
.collection-overview {
    margin: 0 0 30px;
}

.collection-overview-heading {
    margin-bottom: 14px;
}

.collection-overview-heading h2 {
    margin: 5px 0 0;

    font-size: 20px;
}

.collection-overview-grid {
    display: grid;

    grid-template-columns:
        repeat(
            4,
            minmax(0, 1fr)
        );

    gap: 12px;
}

.collection-overview-card {
    display: flex;
    flex-direction: column;

    min-width: 0;
    min-height: 118px;

    padding: 17px;

    box-sizing: border-box;

    border: 1px solid var(--mezha);
    border-radius: 11px;

    background:
        var(--poverkhna-svitla);
}

.collection-overview-label {
    margin-bottom: 11px;

    color:
        var(--tekst-drugoryadnyi);

    font-size: 11px;
    font-weight: 700;

    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.collection-overview-value {
    color:
        var(--morskyi-hlybokyi);

    font-size: 25px;
    line-height: 1.1;
}

.collection-overview-formats {
    color:
        var(--morskyi-hlybokyi);

    font-size: 17px;
    line-height: 1.35;

    overflow-wrap: anywhere;
}

.collection-overview-note {
    margin-top: auto;
    padding-top: 10px;

    color:
        var(--tekst-drugoryadnyi);

    font-size: 12px;
    line-height: 1.45;
}

@media (max-width: 900px) {
    .collection-overview-grid {
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }
}

@media (max-width: 520px) {
    .collection-overview-grid {
        grid-template-columns: 1fr;
    }
}
</style>
