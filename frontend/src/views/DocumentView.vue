<script setup>
import {
    computed,
    nextTick,
    onMounted,
    ref,
    watch
} from "vue"

import {
    useRoute,
    useRouter
} from "vue-router"

import {
    deleteDocument,
    getCollection,
    getDocument,
    getDocumentContentUrl,
    getDocumentDownloadUrl
} from "../api/index.js"

import AppBreadcrumbs from "../components/common/AppBreadcrumbs.vue"

import {
    addRecentDocument
} from "../utils/recentItems.js"

import {
    isFavorite,
    toggleFavorite
} from "../utils/favoriteItems.js"

import {
    useAuth
} from "../composables/useAuth.js"

const route = useRoute()
const router = useRouter()

const {
    currentUser
} = useAuth()

const collectionId =
    Number(route.params.collectionId)

const documentId =
    Number(route.params.documentId)

const document = ref(null)
const collection = ref(null)
const loading = ref(true)

const breadcrumbs = computed(
    () => [
        {
            label: "\u041a\u043e\u043b\u0435\u043a\u0446\u0456\u0457",
            to: {
                name: "collections"
            }
        },
        {
            label:
                collection.value?.name
                || "\u041a\u043e\u043b\u0435\u043a\u0446\u0456\u044f",
            to: {
                name: "collection-detail",
                params: {
                    collectionId
                }
            }
        },
        {
            label:
                document.value?.original_name
                || "\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442",
            current: true
        }
    ]
)
const deleting = ref(false)
const errorMessage = ref("")

const deleteModal = ref(null)

const documentFavorite =
    ref(false)

const textSearchQuery = ref("")
const activeTextMatch = ref(0)

const textMatches = computed(
    () => {
        const source =
            document.value?.extracted_text
            || ""

        const query =
            textSearchQuery.value.trim()

        if (
            !source
            || !query
        ) {
            return []
        }

        const sourceLower =
            source.toLocaleLowerCase(
                "uk-UA"
            )

        const queryLower =
            query.toLocaleLowerCase(
                "uk-UA"
            )

        const matches = []

        let position = 0

        while (
            position < source.length
        ) {
            const index =
                sourceLower.indexOf(
                    queryLower,
                    position
                )

            if (index < 0) {
                break
            }

            matches.push({
                start: index,
                end:
                    index
                    + query.length
            })

            position =
                index
                + Math.max(
                    query.length,
                    1
                )
        }

        return matches
    }
)


const highlightedDocumentParts = computed(
    () => {
        const source =
            document.value?.extracted_text
            || ""

        const matches =
            textMatches.value

        if (!matches.length) {
            return [
                {
                    text: source,
                    match: false,
                    index: -1
                }
            ]
        }

        const parts = []

        let cursor = 0

        matches.forEach(
            (match, index) => {
                if (
                    match.start > cursor
                ) {
                    parts.push({
                        text:
                            source.slice(
                                cursor,
                                match.start
                            ),
                        match: false,
                        index: -1
                    })
                }

                parts.push({
                    text:
                        source.slice(
                            match.start,
                            match.end
                        ),
                    match: true,
                    index
                })

                cursor =
                    match.end
            }
        )

        if (
            cursor < source.length
        ) {
            parts.push({
                text:
                    source.slice(
                        cursor
                    ),
                match: false,
                index: -1
            })
        }

        return parts
    }
)


watch(
    textSearchQuery,
    () => {
        activeTextMatch.value = 0

        nextTick(
            () => {
                scrollToActiveMatch()
            }
        )
    }
)


function scrollToActiveMatch() {
    if (
        !textMatches.value.length
    ) {
        return
    }

    const element =
        window.document.querySelector(
            '[data-document-match="'
            + activeTextMatch.value
            + '"]'
        )

    element?.scrollIntoView({
        behavior: "smooth",
        block: "center"
    })
}


function selectTextMatch(
    index
) {
    const count =
        textMatches.value.length

    if (!count) {
        return
    }

    activeTextMatch.value =
        (
            index
            + count
        ) % count

    nextTick(
        scrollToActiveMatch
    )
}


function previousTextMatch() {
    selectTextMatch(
        activeTextMatch.value - 1
    )
}


function nextTextMatch() {
    selectTextMatch(
        activeTextMatch.value + 1
    )
}


function clearTextSearch() {
    textSearchQuery.value = ""
    activeTextMatch.value = 0
}

const extension = computed(
    () => {
        const name =
            document.value?.original_name || ""

        const parts =
            name.toLowerCase().split(".")

        return (
            parts.length > 1
                ? parts.pop()
                : ""
        )
    }
)

const contentUrl = computed(
    () => getDocumentContentUrl(
        collectionId,
        documentId
    )
)

const downloadUrl = computed(
    () => getDocumentDownloadUrl(
        collectionId,
        documentId
    )
)

function formatMegabytes(bytes) {
    return (
        Number(bytes || 0)
        / 1024
        / 1024
    ).toFixed(2)
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


function formatDate(
    value
) {
    if (!value) {
        return "—"
    }

    const date =
        new Date(value)

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "—"
    }

    return new Intl.DateTimeFormat(
        "uk-UA",
        {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    ).format(date)
}

async function loadDocument() {
    loading.value = true
    errorMessage.value = ""

    try {
        const [
            loadedDocument,
            loadedCollection
        ] = await Promise.all([
            getDocument(
                collectionId,
                documentId
            ),
            getCollection(
                collectionId
            )
        ])

        document.value =
            loadedDocument

        collection.value =
            loadedCollection

        syncDocumentFavorite()

        addRecentDocument(
            collectionId,
            document.value
        )

        document.title =
            `${document.value.original_name} — KnowledgeHub`
    }
    catch (error) {
        errorMessage.value =
            error.message
    }
    finally {
        loading.value = false
    }
}

function syncDocumentFavorite() {
    if (
        !currentUser.value
        || !document.value
    ) {
        documentFavorite.value =
            false

        return
    }

    documentFavorite.value =
        isFavorite(
            currentUser.value.id,
            {
                type: "document",
                id:
                    document.value.id,
                collectionId
            }
        )
}


function toggleDocumentFavorite() {
    if (
        !currentUser.value
        || !document.value
    ) {
        return
    }

    documentFavorite.value =
        toggleFavorite(
            currentUser.value.id,
            {
                type: "document",
                id:
                    document.value.id,
                collectionId,
                name:
                    document.value
                        .original_name,
                collectionName:
                    collection.value?.name
                    || ""
            }
        )
}


function openDeleteModal() {
    deleteModal.value?.showModal()
}

function closeDeleteModal() {
    deleteModal.value?.close()
}

function closeOnBackdrop(event) {
    if (
        event.target === deleteModal.value
    ) {
        closeDeleteModal()
    }
}

async function submitDelete() {
    deleting.value = true
    errorMessage.value = ""

    try {
        await deleteDocument(
            collectionId,
            documentId
        )

        await router.push({
            name: "collection-detail",
            params: {
                collectionId
            }
        })
    }
    catch (error) {
        errorMessage.value =
            error.message

        closeDeleteModal()
    }
    finally {
        deleting.value = false
    }
}

onMounted(
    loadDocument
)
</script>

<template>
    <section
        v-if="loading"
        class="document-view-page"
    >
        <div class="document-preview-empty">
            <h3>
                Завантаження документа...
            </h3>
        </div>
    </section>

    <section
        v-else-if="errorMessage"
        class="error-page"
    >
        <div class="error-card">
            <div class="error-code">
                404
            </div>

            <p class="eyebrow">
                KNOWLEDGEHUB
            </p>

            <h1>
                Документ не знайдено
            </h1>

            <p class="error-description">
                {{ errorMessage }}
            </p>

            <div class="error-actions">
                <RouterLink
                    class="error-primary-button"
                    :to="{
                        name: 'collection-detail',
                        params: {
                            collectionId
                        }
                    }"
                >
                    До колекції
                </RouterLink>

                <RouterLink
                    class="error-secondary-button"
                    :to="{ name: 'home' }"
                >
                    На головну
                </RouterLink>
            </div>
        </div>
    </section>

    <section
        v-else-if="document"
        class="document-view-page"
    >
        <AppBreadcrumbs
            :items="breadcrumbs"
        />

        <header class="document-view-header">
            <div>
                <p class="eyebrow">
                    ДОКУМЕНТ
                </p>

                <h1>
                    {{ document.original_name }}
                </h1>

                <p class="document-header-summary">
                    Документ із колекції
                    <strong>
                        {{ collection?.name || "—" }}
                    </strong>
                </p>
            </div>

            <div class="document-header-actions">
                <button
                    class="secondary-button"
                    type="button"
                    :aria-pressed="
                        documentFavorite
                    "
                    @click="toggleDocumentFavorite"
                >
                    {{
                        documentFavorite
                            ? "★ В обраному"
                            : "☆ В обране"
                    }}
                </button>

                <a
                    class="document-download-button"
                    :href="downloadUrl"
                >
                    Завантажити оригінал
                </a>

                <button
                    class="document-delete-button"
                    type="button"
                    @click="openDeleteModal"
                >
                    Видалити
                </button>
            </div>
        </header>

        <section class="document-details-card">
            <div class="document-details-heading">
                <div>
                    <p class="eyebrow">
                        METADATA
                    </p>

                    <h2>
                        Інформація про документ
                    </h2>
                </div>

                <span
                    class="document-status-badge"
                    :class="
                        'status-'
                        + document.processing_status
                    "
                >
                    {{
                        documentStatusLabel(
                            document.processing_status
                        )
                    }}
                </span>
            </div>

            <dl class="document-details-grid">
                <div class="document-detail-item">
                    <dt>
                        Формат
                    </dt>

                    <dd>
                        {{ extension.toUpperCase() || "—" }}
                    </dd>
                </div>

                <div class="document-detail-item">
                    <dt>
                        Розмір
                    </dt>

                    <dd>
                        {{ formatMegabytes(document.size_bytes) }}
                        МБ
                    </dd>
                </div>

                <div class="document-detail-item">
                    <dt>
                        MIME-type
                    </dt>

                    <dd>
                        {{ document.mime_type || "—" }}
                    </dd>
                </div>

                <div class="document-detail-item">
                    <dt>
                        Додано
                    </dt>

                    <dd>
                        {{ formatDate(document.created_at) }}
                    </dd>
                </div>

                <div class="document-detail-item">
                    <dt>
                        Колекція
                    </dt>

                    <dd>
                        <RouterLink
                            :to="{
                                name: 'collection-detail',
                                params: {
                                    collectionId
                                }
                            }"
                        >
                            {{ collection?.name || "—" }}
                        </RouterLink>
                    </dd>
                </div>

                <div class="document-detail-item">
                    <dt>
                        Статус обробки
                    </dt>

                    <dd>
                        {{
                            documentStatusLabel(
                                document.processing_status
                            )
                        }}
                    </dd>
                </div>
            </dl>

            <div
                v-if="
                    document.processing_status === 'error'
                    && document.processing_error
                "
                class="document-processing-error"
            >
                <strong>
                    Помилка обробки
                </strong>

                <p>
                    {{ document.processing_error }}
                </p>
            </div>
        </section>

        <section
            v-if="extension === 'pdf'"
            class="document-preview-section"
        >
            <div class="document-section-title">
                <h2>
                    Перегляд PDF
                </h2>

                <a
                    :href="contentUrl"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Відкрити в новій вкладці
                </a>
            </div>

            <iframe
                class="pdf-viewer"
                :src="contentUrl"
                :title="document.original_name"
            ></iframe>
        </section>

        <section
            v-else-if="
                extension === 'txt'
                || extension === 'docx'
            "
            class="document-preview-section"
        >
            <div class="document-section-title">
                <h2>
                    Текст документа
                </h2>
            </div>

            <template
                v-if="document.extracted_text"
            >
                <div class="document-text-search">
                    <div class="document-text-search-field">
                        <label for="document-text-search-input">
                            Пошук у документі
                        </label>

                        <input
                            id="document-text-search-input"
                            v-model="textSearchQuery"
                            type="search"
                            placeholder="Введіть слово або фразу..."
                            autocomplete="off"
                            @keydown.enter.prevent="
                                nextTextMatch
                            "
                        />
                    </div>

                    <div
                        v-if="textSearchQuery.trim()"
                        class="document-text-search-navigation"
                    >
                        <span class="document-text-search-count">
                            <template
                                v-if="textMatches.length"
                            >
                                {{
                                    activeTextMatch + 1
                                }}
                                /
                                {{
                                    textMatches.length
                                }}
                            </template>

                            <template v-else>
                                0 збігів
                            </template>
                        </span>

                        <button
                            type="button"
                            :disabled="
                                !textMatches.length
                            "
                            aria-label="Попередній збіг"
                            @click="previousTextMatch"
                        >
                            ↑
                        </button>

                        <button
                            type="button"
                            :disabled="
                                !textMatches.length
                            "
                            aria-label="Наступний збіг"
                            @click="nextTextMatch"
                        >
                            ↓
                        </button>

                        <button
                            class="document-text-search-clear"
                            type="button"
                            @click="clearTextSearch"
                        >
                            Очистити
                        </button>
                    </div>
                </div>

                <div class="document-text-view">
                    <pre><template
                        v-for="(part, index) in highlightedDocumentParts"
                        :key="index"
                    ><mark
                        v-if="part.match"
                        class="document-text-match"
                        :class="{
                            active:
                                part.index
                                === activeTextMatch
                        }"
                        :data-document-match="
                            part.index
                        "
                    >{{ part.text }}</mark><template
                        v-else
                    >{{ part.text }}</template></template></pre>
                </div>
            </template>

            <div
                v-else-if="
                    document.processing_status === 'error'
                "
                class="document-preview-empty"
            >
                <h3>
                    Не вдалося отримати текст
                </h3>

                <p>
                    {{ document.processing_error }}
                </p>
            </div>

            <div
                v-else
                class="document-preview-empty"
            >
                <h3>
                    Текст документа відсутній
                </h3>
            </div>
        </section>

        <dialog
            ref="deleteModal"
            class="document-delete-modal"
            @click="closeOnBackdrop"
        >
            <div class="document-delete-content">
                <div class="document-delete-header">
                    <div>
                        <p class="eyebrow">
                            НЕБЕЗПЕЧНА ДІЯ
                        </p>

                        <h2>
                            Видалити документ?
                        </h2>
                    </div>

                    <button
                        class="document-delete-close"
                        type="button"
                        aria-label="Закрити"
                        @click="closeDeleteModal"
                    >
                        ×
                    </button>
                </div>

                <div class="document-delete-warning">
                    <p>
                        Документ
                        <strong>
                            «{{ document.original_name }}»
                        </strong>
                        буде видалено.
                    </p>

                    <p>
                        Буде видалено і запис
                        у базі даних, і сам файл.
                    </p>

                    <p>
                        Цю дію неможливо скасувати.
                    </p>
                </div>

                <form @submit.prevent="submitDelete">
                    <div class="document-delete-actions">
                        <button
                            class="document-cancel-button"
                            type="button"
                            @click="closeDeleteModal"
                        >
                            Скасувати
                        </button>

                        <button
                            class="document-delete-confirm"
                            type="submit"
                            :disabled="deleting"
                        >
                            {{
                                deleting
                                    ? "Видалення..."
                                    : "Видалити назавжди"
                            }}
                        </button>
                    </div>
                </form>
            </div>
        </dialog>
    </section>
</template>
