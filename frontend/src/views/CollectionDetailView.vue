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
    deleteCollection,
    getCollection,
    getDocuments,
    searchCollection,
    updateCollection,
    uploadDocument
} from "../api/index.js"

const route = useRoute()
const router = useRouter()

const collectionId = computed(
    () => Number(
        route.params.collectionId
    )
)

const collection = ref(null)
const documents = ref([])
const loading = ref(true)

const errors = ref([])
const successMessage = ref("")

const searchMode = ref(
    typeof route.query.mode === "string"
        ? route.query.mode
        : (
            localStorage.getItem(
                "knowledgehub.searchMode"
            ) || "hybrid"
        )
)

const searchQuery = ref(
    typeof route.query.q === "string"
        ? route.query.q
        : (
            localStorage.getItem(
                "knowledgehub.searchQuery"
            ) || ""
        )
)

const searchActive = ref(false)
const searching = ref(false)
const searchResults = ref([])

const uploadModal = ref(null)
const editModal = ref(null)
const deleteModal = ref(null)
const fileInput = ref(null)

const selectedFile = ref(null)
const uploading = ref(false)

const editName = ref("")
const editDescription = ref("")
const saving = ref(false)
const deleting = ref(false)

const searchModeHelp = computed(
    () => {
        const descriptions = {
            lexical:
                "Lexical шукає точні збіги слів і фраз у текстах документів.",

            semantic:
                "Semantic шукає документи зі схожим змістом, навіть якщо слова запиту не збігаються буквально.",

            hybrid:
                "Hybrid поєднує пошук за словами та за змістом. Це основний рекомендований режим KnowledgeHub."
        }

        return descriptions[
            searchMode.value
        ] || ""
    }
)

const visibleDocuments = computed(
    () => {
        if (searchActive.value) {
            return searchResults.value.map(
                result => result.document
            )
        }

        return documents.value
    }
)

const scoreMap = computed(
    () => {
        return Object.fromEntries(
            searchResults.value.map(
                result => [
                    result.document.id,
                    result.score
                ]
            )
        )
    }
)

function clearMessages() {
    errors.value = []
    successMessage.value = ""
}

function formatMegabytes(bytes) {
    return (
        Number(bytes || 0)
        / 1024
        / 1024
    ).toFixed(2)
}

function documentType(document) {
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

function relevanceDescription() {
    if (searchMode.value === "lexical") {
        return [
            "Значення показує, наскільки добре слова запиту збігаються з текстом документа."
        ]
    }

    if (searchMode.value === "semantic") {
        return [
            "Значення базується на семантичній схожості між запитом і змістом документа."
        ]
    }

    return [
        "Значення об'єднує lexical та semantic оцінки.",
        "Поточні ваги: 30% lexical + 70% semantic."
    ]
}

async function loadCollection() {
    loading.value = true
    clearMessages()

    try {
        collection.value =
            await getCollection(
                collectionId.value
            )

        documents.value =
            await getDocuments(
                collectionId.value
            )

        editName.value =
            collection.value.name

        editDescription.value =
            collection.value.description || ""

        localStorage.setItem(
            "knowledgehub.selectedCollectionId",
            String(collectionId.value)
        )

        document.title =
            `${collection.value.name} — KnowledgeHub`
    }
    catch (error) {
        if (error.status === 404) {
            await router.replace({
                name: "collections"
            })

            return
        }

        errors.value = [
            error.message
        ]
    }
    finally {
        loading.value = false
    }
}

async function runSearch({
    updateUrl = true
} = {}) {
    const query =
        searchQuery.value.trim()

    if (!query) {
        errors.value = [
            "Введіть пошуковий запит."
        ]

        return
    }

    searching.value = true
    clearMessages()

    try {
        const data =
            await searchCollection(
                collectionId.value,
                query,
                searchMode.value
            )

        searchResults.value =
            data.results || []

        searchActive.value = true

        localStorage.setItem(
            "knowledgehub.searchMode",
            searchMode.value
        )

        localStorage.setItem(
            "knowledgehub.searchQuery",
            query
        )

        if (updateUrl) {
            await router.replace({
                name: "collection-detail",
                params: {
                    collectionId:
                        collectionId.value
                },
                query: {
                    q: query,
                    mode: searchMode.value
                }
            })
        }
    }
    catch (error) {
        errors.value = [
            error.message
        ]
    }
    finally {
        searching.value = false
    }
}

async function clearSearch() {
    searchActive.value = false
    searchResults.value = []
    searchQuery.value = ""

    localStorage.setItem(
        "knowledgehub.searchQuery",
        ""
    )

    await router.replace({
        name: "collection-detail",
        params: {
            collectionId:
                collectionId.value
        }
    })
}

function openUploadModal() {
    clearMessages()
    uploadModal.value?.showModal()

    nextTick(
        () => fileInput.value?.focus()
    )
}

function openEditModal() {
    clearMessages()

    editName.value =
        collection.value?.name || ""

    editDescription.value =
        collection.value?.description || ""

    editModal.value?.showModal()
}

function openDeleteModal() {
    clearMessages()
    deleteModal.value?.showModal()
}

function closeDialog(dialog) {
    dialog?.close()
}

function closeOnBackdrop(
    event,
    dialog
) {
    if (event.target === dialog) {
        dialog.close()
    }
}

function selectFile(event) {
    selectedFile.value =
        event.target.files?.[0]
        || null
}

async function submitUpload() {
    if (!selectedFile.value) {
        errors.value = [
            "Спочатку виберіть файл."
        ]

        return
    }

    uploading.value = true
    clearMessages()

    try {
        await uploadDocument(
            collectionId.value,
            selectedFile.value
        )

        selectedFile.value = null

        if (fileInput.value) {
            fileInput.value.value = ""
        }

        uploadModal.value?.close()

        successMessage.value =
            "Документ успішно завантажено."

        documents.value =
            await getDocuments(
                collectionId.value
            )

        window.setTimeout(
            async () => {
                try {
                    documents.value =
                        await getDocuments(
                            collectionId.value
                        )
                }
                catch {
                    // Нічого не робимо.
                }
            },
            1200
        )
    }
    catch (error) {
        if (error.status === 413) {
            errors.value = [
                "Файл перевищує максимально дозволений розмір 10 МБ."
            ]
        }
        else if (error.status === 400) {
            errors.value = [
                "Некоректний файл. Дозволені PDF, DOCX та TXT."
            ]
        }
        else {
            errors.value = [
                "Не вдалося завантажити файл."
            ]
        }
    }
    finally {
        uploading.value = false
    }
}

async function submitEdit() {
    saving.value = true
    clearMessages()

    try {
        collection.value =
            await updateCollection(
                collectionId.value,
                {
                    name: editName.value,
                    description:
                        editDescription.value
                            .trim() || null
                }
            )

        editModal.value?.close()

        successMessage.value =
            "Колекцію успішно оновлено."

        document.title =
            `${collection.value.name} — KnowledgeHub`
    }
    catch (error) {
        errors.value = [
            "Перевірте назву та опис колекції."
        ]
    }
    finally {
        saving.value = false
    }
}

async function submitDelete() {
    deleting.value = true
    clearMessages()

    try {
        await deleteCollection(
            collectionId.value
        )

        localStorage.removeItem(
            "knowledgehub.selectedCollectionId"
        )

        await router.push({
            name: "collections"
        })
    }
    catch {
        errors.value = [
            "Не вдалося виконати операцію з колекцією."
        ]

        deleteModal.value?.close()
    }
    finally {
        deleting.value = false
    }
}

watch(
    searchMode,
    value => {
        localStorage.setItem(
            "knowledgehub.searchMode",
            value
        )
    }
)

watch(
    searchQuery,
    value => {
        localStorage.setItem(
            "knowledgehub.searchQuery",
            value
        )
    }
)

onMounted(
    async () => {
        await loadCollection()

        if (
            collection.value
            && searchQuery.value.trim()
        ) {
            await runSearch({
                updateUrl: false
            })
        }
    }
)
</script>

<template>
    <section class="collections-page">
        <RouterLink
            class="back-link"
            :to="{ name: 'collections' }"
        >
            ← Назад до колекцій
        </RouterLink>

        <div
            v-if="loading"
            class="empty-state"
        >
            <h3>
                Завантаження...
            </h3>
        </div>

        <template v-else-if="collection">
            <div class="collection-detail-top">
                <div class="collection-detail-header">
                    <p class="eyebrow">
                        КОЛЕКЦІЯ
                    </p>

                    <h1>
                        {{ collection.name }}
                    </h1>

                    <p v-if="collection.description">
                        {{ collection.description }}
                    </p>

                    <p
                        v-else
                        class="collection-empty"
                    >
                        Опис не додано.
                    </p>
                </div>

                <div class="collection-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        @click="openEditModal"
                    >
                        Редагувати
                    </button>

                    <button
                        class="danger-button"
                        type="button"
                        @click="openDeleteModal"
                    >
                        Видалити
                    </button>
                </div>
            </div>

            <div
                v-if="errors.length"
                class="message message-error"
            >
                <p
                    v-for="error in errors"
                    :key="error"
                >
                    {{ error }}
                </p>
            </div>

            <div
                v-if="successMessage"
                class="message message-success"
            >
                <p>
                    {{ successMessage }}
                </p>
            </div>

            <section class="document-search">
                <div class="search-section-heading">
                    <h2>
                        Пошук у документах
                    </h2>

                    <p>
                        Оберіть спосіб, яким система
                        визначатиме релевантність документів.
                    </p>
                </div>

                <form
                    class="document-search-form"
                    @submit.prevent="runSearch()"
                >
                    <div class="search-mode-field">
                        <div class="label-with-info">
                            <label
                                class="document-search-label"
                                for="search-mode"
                            >
                                Режим
                            </label>

                            <span
                                class="info-tooltip"
                                tabindex="0"
                                aria-label="Інформація про режими пошуку"
                            >
                                <span class="info-icon">
                                    i
                                </span>

                                <span class="tooltip-content">
                                    <strong>
                                        Режими пошуку
                                    </strong>

                                    <span>
                                        <b>Lexical</b> — шукає
                                        збіги конкретних слів
                                        і фраз у тексті.
                                    </span>

                                    <span>
                                        <b>Semantic</b> — шукає
                                        документи зі схожим
                                        змістом, навіть якщо
                                        використані інші слова.
                                    </span>

                                    <span>
                                        <b>Hybrid</b> — поєднує
                                        пошук за словами
                                        та пошук за змістом.
                                    </span>
                                </span>
                            </span>
                        </div>

                        <select
                            id="search-mode"
                            v-model="searchMode"
                            class="search-mode-select"
                            name="mode"
                        >
                            <option value="hybrid">
                                Hybrid
                            </option>

                            <option value="semantic">
                                Semantic
                            </option>

                            <option value="lexical">
                                Lexical
                            </option>
                        </select>
                    </div>

                    <div class="document-search-field">
                        <label
                            class="document-search-label"
                            for="document-search-input"
                        >
                            Запит
                        </label>

                        <input
                            id="document-search-input"
                            v-model="searchQuery"
                            class="document-search-input"
                            name="q"
                            type="search"
                            maxlength="200"
                            autocomplete="off"
                            placeholder="Наприклад: BM25, embeddings, RAG..."
                        >
                    </div>

                    <button
                        class="document-search-button"
                        type="submit"
                        :disabled="searching"
                    >
                        {{
                            searching
                                ? "Пошук..."
                                : "Знайти"
                        }}
                    </button>
                </form>

                <div
                    class="search-mode-help"
                    aria-live="polite"
                >
                    {{ searchModeHelp }}
                </div>

                <div
                    v-if="searchActive"
                    class="search-summary"
                >
                    <div>
                        Знайдено:
                        <strong>
                            {{ visibleDocuments.length }}
                        </strong>

                        · режим:

                        <strong>
                            {{
                                searchMode.charAt(0).toUpperCase()
                                + searchMode.slice(1)
                            }}
                        </strong>

                        · запит:

                        <strong>
                            «{{ searchQuery }}»
                        </strong>
                    </div>

                    <a
                        href="#"
                        @click.prevent="clearSearch"
                    >
                        Очистити пошук
                    </a>
                </div>
            </section>

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
                    @click="openUploadModal"
                >
                    + Додати документ
                </button>
            </div>

            <div
                v-if="visibleDocuments.length"
                class="documents-list"
            >
                <article
                    v-for="(documentItem, index) in visibleDocuments"
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
                                        collectionId: collection.id,
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
                                        v-for="text in relevanceDescription()"
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

            <dialog
                ref="uploadModal"
                class="collection-modal"
                @click="
                    closeOnBackdrop(
                        $event,
                        uploadModal
                    )
                "
            >
                <div class="collection-modal-content">
                    <div class="collection-modal-header">
                        <div>
                            <p class="eyebrow">
                                KNOWLEDGEHUB
                            </p>

                            <h2>
                                Додати документ
                            </h2>
                        </div>

                        <button
                            class="modal-close-button"
                            type="button"
                            aria-label="Закрити"
                            @click="
                                closeDialog(
                                    uploadModal
                                )
                            "
                        >
                            ×
                        </button>
                    </div>

                    <form
                        class="standard-form"
                        @submit.prevent="submitUpload"
                    >
                        <div class="form-field">
                            <label for="document-file">
                                Файл
                            </label>

                            <input
                                id="document-file"
                                ref="fileInput"
                                name="document_file"
                                type="file"
                                accept=".pdf,.docx,.txt"
                                required
                                @change="selectFile"
                            >

                            <p class="form-hint">
                                PDF, DOCX або TXT.
                                До 10 МБ.
                            </p>
                        </div>

                        <div class="collection-modal-actions">
                            <button
                                class="secondary-button"
                                type="button"
                                @click="
                                    closeDialog(
                                        uploadModal
                                    )
                                "
                            >
                                Скасувати
                            </button>

                            <button
                                class="form-submit"
                                type="submit"
                                :disabled="uploading"
                            >
                                {{
                                    uploading
                                        ? "Завантаження..."
                                        : "Завантажити"
                                }}
                            </button>
                        </div>
                    </form>
                </div>
            </dialog>

            <dialog
                ref="editModal"
                class="collection-modal"
                @click="
                    closeOnBackdrop(
                        $event,
                        editModal
                    )
                "
            >
                <div class="collection-modal-content">
                    <div class="collection-modal-header">
                        <div>
                            <p class="eyebrow">
                                КОЛЕКЦІЯ
                            </p>

                            <h2>
                                Редагувати
                            </h2>
                        </div>

                        <button
                            class="modal-close-button"
                            type="button"
                            aria-label="Закрити"
                            @click="
                                closeDialog(
                                    editModal
                                )
                            "
                        >
                            ×
                        </button>
                    </div>

                    <form
                        class="standard-form"
                        @submit.prevent="submitEdit"
                    >
                        <div class="form-field">
                            <label for="edit-collection-name">
                                Назва
                            </label>

                            <input
                                id="edit-collection-name"
                                v-model="editName"
                                name="name"
                                type="text"
                                maxlength="100"
                                required
                            >
                        </div>

                        <div class="form-field">
                            <label for="edit-collection-description">
                                Опис
                            </label>

                            <textarea
                                id="edit-collection-description"
                                v-model="editDescription"
                                name="description"
                                maxlength="1000"
                                rows="5"
                            ></textarea>
                        </div>

                        <div class="collection-modal-actions">
                            <button
                                class="secondary-button"
                                type="button"
                                @click="
                                    closeDialog(
                                        editModal
                                    )
                                "
                            >
                                Скасувати
                            </button>

                            <button
                                class="form-submit"
                                type="submit"
                                :disabled="saving"
                            >
                                {{
                                    saving
                                        ? "Збереження..."
                                        : "Зберегти"
                                }}
                            </button>
                        </div>
                    </form>
                </div>
            </dialog>

            <dialog
                ref="deleteModal"
                class="collection-modal delete-modal"
                @click="
                    closeOnBackdrop(
                        $event,
                        deleteModal
                    )
                "
            >
                <div class="collection-modal-content">
                    <div class="collection-modal-header">
                        <div>
                            <p class="eyebrow">
                                НЕБЕЗПЕЧНА ДІЯ
                            </p>

                            <h2>
                                Видалити колекцію?
                            </h2>
                        </div>

                        <button
                            class="modal-close-button"
                            type="button"
                            aria-label="Закрити"
                            @click="
                                closeDialog(
                                    deleteModal
                                )
                            "
                        >
                            ×
                        </button>
                    </div>

                    <div class="delete-warning">
                        <p>
                            Колекція
                            <strong>
                                «{{ collection.name }}»
                            </strong>
                            буде видалена разом
                            з усіма її документами.
                        </p>

                        <p>
                            Цю дію неможливо скасувати.
                        </p>
                    </div>

                    <form @submit.prevent="submitDelete">
                        <div class="collection-modal-actions">
                            <button
                                class="secondary-button"
                                type="button"
                                @click="
                                    closeDialog(
                                        deleteModal
                                    )
                                "
                            >
                                Скасувати
                            </button>

                            <button
                                class="danger-button"
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
        </template>
    </section>
</template>
