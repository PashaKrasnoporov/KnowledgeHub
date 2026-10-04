<script setup>
import {
    computed,
    onMounted,
    ref,
    watch
} from "vue"

import {
    useRoute,
    useRouter
} from "vue-router"

import CollectionDeleteDialog from "../components/collections/CollectionDeleteDialog.vue"
import CollectionEditDialog from "../components/collections/CollectionEditDialog.vue"
import CollectionHeader from "../components/collections/CollectionHeader.vue"
import FeedbackMessages from "../components/common/FeedbackMessages.vue"
import DocumentsList from "../components/documents/DocumentsList.vue"
import DocumentUploadDialog from "../components/documents/DocumentUploadDialog.vue"
import ResearchPanel from "../components/research/ResearchPanel.vue"
import DocumentSearchPanel from "../components/search/DocumentSearchPanel.vue"

import {
    getCollection,
    getDocuments,
    searchCollection
} from "../api/index.js"

const route = useRoute()
const router = useRouter()

const cloudLite = (
    import.meta.env.VITE_DEPLOYMENT_PROFILE
    === "railway-lite"
)

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
    cloudLite
        ? "lexical"
        : (
            typeof route.query.mode === "string"
                ? route.query.mode
                : (
                    localStorage.getItem(
                        "knowledgehub.searchMode"
                    ) || "hybrid"
                )
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

const uploadDialog = ref(null)
const editDialog = ref(null)
const deleteDialog = ref(null)

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
    () => Object.fromEntries(
        searchResults.value.map(
            result => [
                result.document.id,
                result.score
            ]
        )
    )
)

function clearMessages() {
    errors.value = []
    successMessage.value = ""
}

function showError(
    message
) {
    successMessage.value = ""
    errors.value = [
        message
    ]
}

async function refreshDocuments() {
    documents.value =
        await getDocuments(
            collectionId.value
        )
}

async function loadCollection() {
    loading.value = true
    clearMessages()

    try {
        collection.value =
            await getCollection(
                collectionId.value
            )

        await refreshDocuments()

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

        showError(
            error.message
        )
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
        showError(
            "Введіть пошуковий запит."
        )

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
        showError(
            error.message
        )
    }
    finally {
        searching.value = false
    }
}

async function clearSearch() {
    searchActive.value = false
    searchResults.value = []
    searchQuery.value = ""

    await router.replace({
        name: "collection-detail",
        params: {
            collectionId:
                collectionId.value
        }
    })
}

async function handleUploaded() {
    clearMessages()

    successMessage.value =
        "Документ успішно завантажено."

    await refreshDocuments()

    window.setTimeout(
        async () => {
            try {
                await refreshDocuments()
            }
            catch {
                // Повторне оновлення не критичне.
            }
        },
        1200
    )
}

function handleCollectionSaved(
    updated
) {
    clearMessages()

    collection.value =
        updated

    successMessage.value =
        "Колекцію успішно оновлено."

    document.title =
        `${updated.name} — KnowledgeHub`
}

async function handleCollectionDeleted() {
    localStorage.removeItem(
        "knowledgehub.selectedCollectionId"
    )

    await router.push({
        name: "collections"
    })
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
            <CollectionHeader
                :collection="collection"
                @edit="editDialog?.open()"
                @delete="deleteDialog?.open()"
            />

            <FeedbackMessages
                :errors="errors"
                :success-message="successMessage"
            />

            <DocumentSearchPanel
                v-model:mode="searchMode"
                v-model:query="searchQuery"
                :searching="searching"
                :active="searchActive"
                :result-count="visibleDocuments.length"
                @search="runSearch()"
                @clear="clearSearch"
            />

            <ResearchPanel
                v-if="!cloudLite"
                :collection-id="collectionId"
            />

            <section
                v-else
                class="document-search"
            >
                <div class="search-section-heading">
                    <h2>
                        Дослідницька відповідь
                    </h2>

                    <p>
                        У безкоштовному хмарному профілі
                        важкі ML/LLM-функції вимкнено.
                        Для лабораторної №4 доступні
                        автентифікація, колекції,
                        документи, REST API і
                        лексичний пошук.
                    </p>
                </div>
            </section>

            <DocumentsList
                :collection-id="collectionId"
                :documents="visibleDocuments"
                :search-active="searchActive"
                :score-map="scoreMap"
                :search-mode="searchMode"
                @upload="uploadDialog?.open()"
            />

            <DocumentUploadDialog
                ref="uploadDialog"
                :collection-id="collectionId"
                @uploaded="handleUploaded"
                @error="showError"
            />

            <CollectionEditDialog
                ref="editDialog"
                :collection="collection"
                @saved="handleCollectionSaved"
                @error="showError"
            />

            <CollectionDeleteDialog
                ref="deleteDialog"
                :collection="collection"
                @deleted="handleCollectionDeleted"
                @error="showError"
            />
        </template>
    </section>
</template>
