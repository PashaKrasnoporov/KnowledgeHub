<script setup>
import {
    computed,
    ref
} from "vue"

import {
    useAuth
} from "../../composables/useAuth.js"

import {
    isFavorite,
    toggleFavorite
} from "../../utils/favoriteItems.js"

const props = defineProps({
    collectionId: {
        type: Number,
        required: true
    },

    collectionName: {
        type: String,
        default: ""
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

const {
    currentUser
} = useAuth()

const favoriteVersion = ref(0)
const onlyFavorites = ref(false)

const typeFilter = ref("all")
const statusFilter = ref("all")
const sortMode = ref("default")

const displayedDocuments = computed(
    () => {
        let result =
            props.documents.filter(
                document => {
                    const typeMatches =
                        typeFilter.value === "all"
                        || documentType(document).toLowerCase()
                            === typeFilter.value

                    const statusMatches =
                        statusFilter.value === "all"
                        || document.processing_status
                            === statusFilter.value

                    const favoriteMatches =
                        !onlyFavorites.value
                        || documentIsFavorite(
                            document
                        )

                    return (
                        typeMatches
                        && statusMatches
                        && favoriteMatches
                    )
                }
            )

        result = [
            ...result
        ]

        if (
            sortMode.value === "default"
            && props.searchActive
        ) {
            return result
        }

        const mode =
            sortMode.value === "default"
                ? "created-desc"
                : sortMode.value

        result.sort(
            (a, b) => {
                if (mode === "name-asc") {
                    return a.original_name.localeCompare(
                        b.original_name,
                        "uk-UA"
                    )
                }

                if (mode === "name-desc") {
                    return b.original_name.localeCompare(
                        a.original_name,
                        "uk-UA"
                    )
                }

                if (mode === "size-asc") {
                    return (
                        Number(a.size_bytes || 0)
                        - Number(b.size_bytes || 0)
                    )
                }

                if (mode === "size-desc") {
                    return (
                        Number(b.size_bytes || 0)
                        - Number(a.size_bytes || 0)
                    )
                }

                const aDate =
                    new Date(
                        a.created_at || 0
                    ).getTime()

                const bDate =
                    new Date(
                        b.created_at || 0
                    ).getTime()

                if (mode === "created-asc") {
                    return aDate - bDate
                }

                return bDate - aDate
            }
        )

        return result
    }
)


const filtersActive = computed(
    () => (
        typeFilter.value !== "all"
        || statusFilter.value !== "all"
        || sortMode.value !== "default"
        || onlyFavorites.value
    )
)


function resetFilters() {
    typeFilter.value = "all"
    statusFilter.value = "all"
    sortMode.value = "default"
    onlyFavorites.value = false
}


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


function documentIsFavorite(
    documentItem
) {
    favoriteVersion.value

    if (!currentUser.value) {
        return false
    }

    return isFavorite(
        currentUser.value.id,
        {
            type: "document",
            id: documentItem.id,
            collectionId:
                props.collectionId
        }
    )
}


function toggleDocumentFavorite(
    documentItem
) {
    if (!currentUser.value) {
        return
    }

    toggleFavorite(
        currentUser.value.id,
        {
            type: "document",
            id: documentItem.id,
            collectionId:
                props.collectionId,
            name:
                documentItem.original_name,
            collectionName:
                props.collectionName
        }
    )

    favoriteVersion.value += 1
}


function documentStatusLabel(
    status
) {
    if (status === "ready") {
        return "Готовий"
    }

    if (status === "pending") {
        return "Обробляється"
    }

    if (status === "error") {
        return "Помилка"
    }

    return status || "Невідомо"
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

    <section
        v-if="documents.length"
        class="documents-filter-toolbar"
        aria-label="Фільтрування і сортування документів"
    >
        <div class="document-filter-control">
            <label for="document-type-filter">
                Формат
            </label>

            <select
                id="document-type-filter"
                v-model="typeFilter"
            >
                <option value="all">
                    Усі формати
                </option>

                <option value="pdf">
                    PDF
                </option>

                <option value="docx">
                    DOCX
                </option>

                <option value="txt">
                    TXT
                </option>
            </select>
        </div>

        <div class="document-filter-control">
            <label for="document-status-filter">
                Статус
            </label>

            <select
                id="document-status-filter"
                v-model="statusFilter"
            >
                <option value="all">
                    Усі статуси
                </option>

                <option value="ready">
                    Готові
                </option>

                <option value="pending">
                    Обробляються
                </option>

                <option value="error">
                    Помилка
                </option>
            </select>
        </div>

        <div class="document-filter-control document-sort-control">
            <label for="document-sort">
                Сортування
            </label>

            <select
                id="document-sort"
                v-model="sortMode"
            >
                <option value="default">
                    {{
                        searchActive
                            ? "За релевантністю"
                            : "Спочатку нові"
                    }}
                </option>

                <option value="created-desc">
                    Спочатку нові
                </option>

                <option value="created-asc">
                    Спочатку старі
                </option>

                <option value="name-asc">
                    Назва: А–Я
                </option>

                <option value="name-desc">
                    Назва: Я–А
                </option>

                <option value="size-desc">
                    Спочатку більші
                </option>

                <option value="size-asc">
                    Спочатку менші
                </option>
            </select>
        </div>

        <div class="document-favorites-filter">
            <label>
                <input
                    v-model="onlyFavorites"
                    type="checkbox"
                >

                <span>
                    ★ Тільки обране
                </span>
            </label>
        </div>

        <button
            v-if="filtersActive"
            class="document-filter-reset"
            type="button"
            @click="resetFilters"
        >
            Скинути фільтри
        </button>

        <div class="document-filter-summary">
            Показано:
            <strong>
                {{ displayedDocuments.length }}
            </strong>
            із
            <strong>
                {{ documents.length }}
            </strong>
        </div>
    </section>

    <div
        v-if="displayedDocuments.length"
        class="documents-list"
    >
        <article
            v-for="(documentItem, index) in displayedDocuments"
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

            <button
                class="document-card-favorite"
                type="button"
                :aria-pressed="
                    documentIsFavorite(
                        documentItem
                    )
                "
                :aria-label="
                    documentIsFavorite(
                        documentItem
                    )
                        ? 'Прибрати документ з обраного'
                        : 'Додати документ в обране'
                "
                :title="
                    documentIsFavorite(
                        documentItem
                    )
                        ? 'Прибрати з обраного'
                        : 'Додати в обране'
                "
                @click="
                    toggleDocumentFavorite(
                        documentItem
                    )
                "
            >
                {{
                    documentIsFavorite(
                        documentItem
                    )
                        ? "★"
                        : "☆"
                }}
            </button>

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
                    {{
                        documentStatusLabel(
                            documentItem.processing_status
                        )
                    }}
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
        <template
            v-if="
                documents.length
                && filtersActive
            "
        >
            <h3>
                Фільтри не дали результатів
            </h3>

            <p>
                Змініть параметри фільтрації
                або покажіть усі документи.
            </p>

            <button
                class="secondary-button"
                type="button"
                @click="resetFilters"
            >
                Скинути фільтри
            </button>
        </template>

        <template v-else-if="searchActive">
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


<style scoped>
.document-card {
    position: relative;
}

.document-info {
    padding-right: 44px;
}

.document-card-favorite {
    position: absolute;
    top: 15px;
    right: 15px;

    z-index: 2;

    width: 34px;
    height: 34px;

    padding: 0;

    border: 1px solid var(--mezha);
    border-radius: 50%;

    background: var(--poverkhna-svitla);
    color: var(--akvamarin-temnyi);

    font-size: 20px;
    line-height: 1;

    cursor: pointer;
}

.document-card-favorite:hover {
    border-color: var(--mezha-temna);
    background: var(--poverkhna);
}

.document-card-favorite[aria-pressed="true"] {
    color: var(--morskyi-hlybokyi);
}

.documents-filter-toolbar {
    display: grid;
    grid-template-columns:
        minmax(150px, 0.8fr)
        minmax(170px, 0.9fr)
        minmax(210px, 1fr)
        auto;

    gap: 12px;
    align-items: end;

    margin: 0 0 18px;
    padding: 18px;

    border: 1px solid var(--mezha);
    border-radius: 12px;

    background: var(--poverkhna-svitla);
}

.document-filter-control {
    min-width: 0;
}

.document-filter-control label {
    display: block;

    margin-bottom: 7px;

    color: var(--tekst-drugoryadnyi);

    font-size: 12px;
    font-weight: 700;
}

.document-filter-control select {
    width: 100%;
    height: 42px;

    padding: 0 11px;

    border: 1px solid var(--mezha-temna);
    border-radius: 8px;

    background: var(--poverkhna-svitla);
    color: var(--tekst-osnovnyi);

    font: inherit;
    font-size: 14px;
}

.document-filter-control select:focus {
    border-color: var(--focus);

    outline: none;

    box-shadow:
        0 0 0 3px
        rgba(128, 175, 186, 0.15);
}

.document-favorites-filter {
    display: flex;
    align-items: center;

    min-height: 42px;
}

.document-favorites-filter label {
    position: relative;

    display: block;

    cursor: pointer;
}

.document-favorites-filter input {
    position: absolute;

    width: 1px;
    height: 1px;

    opacity: 0;

    pointer-events: none;
}

.document-favorites-filter span {
    display: inline-flex;

    min-height: 44px;

    align-items: center;
    justify-content: center;

    box-sizing: border-box;

    padding: 0 16px;

    border:
        1px solid
        var(--mezha-temna);

    border-radius: 12px;

    background:
        var(--poverkhna-svitla);

    color:
        var(--akvamarin-temnyi);

    font-size: 13px;
    font-weight: 700;

    user-select: none;

    transition:
        background 0.15s ease,
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}

.document-favorites-filter
label:hover span {
    background:
        var(--poverkhna);
}

.document-favorites-filter
input:focus-visible + span {
    outline:
        2px solid
        var(--focus);

    outline-offset: 2px;
}

.document-favorites-filter
input:checked + span {
    border-color:
        var(--akvamarin-temnyi);

    background:
        var(--poverkhna);

    color:
        var(--morskyi-hlybokyi);

    box-shadow:
        inset 0 0 0 1px
        var(--akvamarin-temnyi);
}

.document-filter-reset {
    height: 42px;

    padding: 0 14px;

    border: 1px solid var(--mezha-temna);
    border-radius: 8px;

    background: transparent;
    color: var(--akvamarin-temnyi);

    font: inherit;
    font-size: 13px;
    font-weight: 700;

    cursor: pointer;
}

.document-filter-reset:hover {
    background: var(--poverkhna);
}

.document-filter-summary {
    grid-column: 1 / -1;

    padding-top: 4px;

    color: var(--tekst-drugoryadnyi);

    font-size: 13px;
}

.document-filter-summary strong {
    color: var(--morskyi-hlybokyi);
}

@media (max-width: 820px) {
    .documents-filter-toolbar {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .document-filter-reset {
        width: 100%;
    }
}

@media (max-width: 560px) {
    .documents-filter-toolbar {
        grid-template-columns: 1fr;
    }

    .document-filter-summary {
        grid-column: auto;
    }
}
</style>
