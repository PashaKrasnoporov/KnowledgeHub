<script setup>
import {
    computed,
    onMounted,
    ref
} from "vue"

import {
    useRoute,
    useRouter
} from "vue-router"

import {
    deleteDocument,
    getDocument,
    getDocumentContentUrl,
    getDocumentDownloadUrl
} from "../api/index.js"

const route = useRoute()
const router = useRouter()

const collectionId =
    Number(route.params.collectionId)

const documentId =
    Number(route.params.documentId)

const document = ref(null)
const loading = ref(true)
const deleting = ref(false)
const errorMessage = ref("")

const deleteModal = ref(null)

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

async function loadDocument() {
    loading.value = true
    errorMessage.value = ""

    try {
        document.value =
            await getDocument(
                collectionId,
                documentId
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
        <RouterLink
            class="document-back-link"
            :to="{
                name: 'collection-detail',
                params: {
                    collectionId
                }
            }"
        >
            ← Назад до колекції
        </RouterLink>

        <header class="document-view-header">
            <div>
                <p class="eyebrow">
                    ДОКУМЕНТ
                </p>

                <h1>
                    {{ document.original_name }}
                </h1>

                <div class="document-metadata">
                    <span>
                        Формат:
                        <strong>
                            {{ extension.toUpperCase() }}
                        </strong>
                    </span>

                    <span>
                        Розмір:
                        <strong>
                            {{ formatMegabytes(document.size_bytes) }}
                            МБ
                        </strong>
                    </span>

                    <span>
                        Статус:
                        <strong>
                            {{ document.processing_status }}
                        </strong>
                    </span>
                </div>
            </div>

            <div class="document-header-actions">
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

            <div
                v-if="document.extracted_text"
                class="document-text-view"
            >
                <pre>{{ document.extracted_text }}</pre>
            </div>

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
