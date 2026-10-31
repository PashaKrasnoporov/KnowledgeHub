<script setup>
import {
    computed
} from "vue"

const props = defineProps({
    collectionId: {
        type: Number,
        required: true
    },

    documents: {
        type: Array,
        default: () => []
    },

    searchActive: {
        type: Boolean,
        default: false
    },

    scoreMap: {
        type: Object,
        default: () => ({})
    },

    snippetMap: {
        type: Object,
        default: () => ({})
    },

    searchQuery: {
        type: String,
        default: ""
    },

    searchMode: {
        type: String,
        default: "hybrid"
    }
})

defineEmits([
    "upload"
])

const relevanceDescription = computed(
    () => {
        if (props.searchMode === "lexical") {
            return [
                "Значення показує, наскільки добре слова запиту збігаються з текстом документа."
            ]
        }

        if (props.searchMode === "semantic") {
            return [
                "Значення базується на семантичній схожості між запитом і змістом документа."
            ]
        }

        return [
            "Значення об'єднує lexical та semantic оцінки.",
            "Поточні ваги: 30% lexical + 70% semantic."
        ]
    }
)

function formatMegabytes(
    bytes
) {
    return (
        Number(bytes || 0)
        / 1024
        / 1024
    ).toFixed(2)
}

function highlightSnippet(
    value
) {
    if (!value) {
        return []
    }

    const terms = [
        ...new Set(
            props.searchQuery
                .trim()
                .split(/\s+/)
                .map(
                    term =>
                        term.toLocaleLowerCase(
                            "uk-UA"
                        )
                )
                .filter(
                    term =>
                        term.length >= 2
                )
        )
    ].sort(
        (a, b) =>
            b.length - a.length
    )

    if (!terms.length) {
        return [
            {
                text: value,
                match: false
            }
        ]
    }

    let parts = [
        {
            text: value,
            match: false
        }
    ]

    for (const term of terms) {
        const nextParts = []

        for (const part of parts) {
            if (part.match) {
                nextParts.push(
                    part
                )

                continue
            }

            let remaining =
                part.text

            while (remaining) {
                const lowered =
                    remaining.toLocaleLowerCase(
                        "uk-UA"
                    )

                const index =
                    lowered.indexOf(
                        term
                    )

                if (index < 0) {
                    nextParts.push({
                        text: remaining,
                        match: false
                    })

                    break
                }

                if (index > 0) {
                    nextParts.push({
                        text:
                            remaining.slice(
                                0,
                                index
                            ),
                        match: false
                    })
                }

                nextParts.push({
                    text:
                        remaining.slice(
                            index,
                            index + term.length
                        ),

                    match: true
                })

                remaining =
                    remaining.slice(
                        index + term.length
                    )
            }
        }

        parts =
            nextParts
    }

    return parts.filter(
        part =>
            part.text
    )
}


function documentType(
    document
) {
    const name =
        document.original_name
            .toLowerCase()

    if (name.endsWith(".pdf")) {
        return "PDF"
    }

    if (name.endsWith(".docx")) {
        return "DOCX"
    }

    return "TXT"
}
</script>

<template>
    <div class="documents-toolbar">
        <div>
            <h2>
                {{
                    searchActive
                        ? "Результати пошуку"
                        : "Документи"
                }}
            </h2>

            <p v-if="!searchActive">
                PDF, DOCX або TXT.
                Максимальний розмір — 10 МБ.
            </p>
        </div>

        <button
            class="new-collection-button"
            type="button"
            @click="$emit('upload')"
        >
            + Додати документ
        </button>
    </div>

    <div
        v-if="documents.length"
        class="documents-list"
    >
        <article
            v-for="(documentItem, index) in documents"
            :key="documentItem.id"
            class="document-card"
        >
            <div
                v-if="searchActive"
                class="search-position"
            >
                {{ index + 1 }}
            </div>

            <div class="document-icon">
                {{ documentType(documentItem) }}
            </div>

            <div class="document-info">
                <h3>
                    <RouterLink
                        class="document-title-link"
                        :to="{
                            name: 'document',
                            params: {
                                collectionId,
                                documentId: documentItem.id
                            }
                        }"
                    >
                        {{ documentItem.original_name }}
                    </RouterLink>
                </h3>

                <p>
                    {{ formatMegabytes(documentItem.size_bytes) }}
                    МБ
                    ·
                    {{ documentItem.processing_status }}
                </p>

                <p
                    v-if="
                        searchActive
                        && snippetMap[documentItem.id]
                    "
                    class="search-snippet"
                >
                    <template
                        v-for="(part, partIndex) in highlightSnippet(
                            snippetMap[documentItem.id]
                        )"
                        :key="partIndex"
                    >
                        <mark
                            v-if="part.match"
                        >
                            {{ part.text }}
                        </mark>

                        <span v-else>
                            {{ part.text }}
                        </span>
                    </template>
                </p>

                <div
                    v-if="searchActive"
                    class="relevance-row"
                >
                    <span>
                        Оцінка релевантності:
                    </span>

                    <strong>
                        {{
                            Number(
                                scoreMap[documentItem.id] || 0
                            ).toFixed(3)
                        }}
                    </strong>

                    <span
                        class="info-tooltip"
                        tabindex="0"
                        aria-label="Що означає оцінка релевантності"
                    >
                        <span class="info-icon small">
                            i
                        </span>

                        <span class="tooltip-content">
                            <strong>
                                Оцінка релевантності
                            </strong>

                            <span
                                v-for="text in relevanceDescription"
                                :key="text"
                            >
                                {{ text }}
                            </span>

                            <span>
                                Більше значення означає
                                вищу релевантність
                                у цьому пошуку.
                                Це не відсоток
                                і не ймовірність.
                            </span>
                        </span>
                    </span>
                </div>
            </div>
        </article>
    </div>

    <div
        v-else
        class="empty-state"
    >
        <template v-if="searchActive">
            <h3>
                Нічого не знайдено
            </h3>

            <p>
                Спробуйте інший запит
                або інший режим пошуку.
            </p>
        </template>

        <template v-else>
            <h3>
                Документів поки немає
            </h3>

            <p>
                Додайте перший документ
                до цієї колекції.
            </p>
        </template>
    </div>
</template>
