<script setup>
import {
    computed,
    onBeforeUnmount,
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
import CollectionOverview from "../components/collections/CollectionOverview.vue"
import AppBreadcrumbs from "../components/common/AppBreadcrumbs.vue"
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

import {
    addRecentCollection,
    removeRecentCollection,
    updateRecentCollection
} from "../utils/recentItems.js"

import {
    removeFavoriteCollection,
    updateFavoriteCollection
} from "../utils/favoriteItems.js"

import {
    useAuth
} from "../composables/useAuth.js"


const route = useRoute()
const router = useRouter()

const {
    currentUser
} = useAuth()

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

const breadcrumbs = computed(
    () => [
        {
            label: "Колекції",
            to: {
                name: "collections"
            }
        },
        {
            label: collection.value?.name || "Колекція",
            current: true
        }
    ]
)

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

localStorage.removeItem(
    "knowledgehub.searchQuery"
)

const searchQuery = ref(
    typeof route.query.q === "string"
        ? route.query.q
        : ""
)

const searchActive = ref(false)
const searching = ref(false)
const searchResults = ref([])

const uploadDialog = ref(null)
const editDialog = ref(null)
const deleteDialog = ref(null)

const activeWorkspace = ref(
    typeof route.query.q === "string"
        ? "search"
        : "documents"
)

let processingPollTimer = null
let processingPollAttempts = 0

const PROCESSING_POLL_INTERVAL = 1500
const PROCESSING_POLL_LIMIT = 30


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


const snippetMap = computed(
    () => Object.fromEntries(
        searchResults.value.map(
            result => [
                result.document.id,
                result.snippet || ""
            ]
        )
    )
)


function clearMessages() {
    errors.value = []
    successMessage.value = ""
}


function showError(message) {
    successMessage.value = ""
    errors.value = [message]
}


async function refreshDocuments() {
    documents.value = await getDocuments(
        collectionId.value
    )
}


function hasProcessingDocuments() {
    return documents.value.some(
        document => (
            document.processing_status === "pending"
            || document.processing_status === "processing"
        )
    )
}


function stopProcessingPolling() {
    if (processingPollTimer !== null) {
        window.clearInterval(
            processingPollTimer
        )

        processingPollTimer = null
    }

    processingPollAttempts = 0
}


function startProcessingPolling() {
    stopProcessingPolling()

    if (!hasProcessingDocuments()) {
        return
    }

    processingPollTimer = window.setInterval(
        async () => {
            processingPollAttempts += 1

            try {
                await refreshDocuments()
            }
            catch {
                // A later polling attempt can recover automatically.
            }

            if (
                !hasProcessingDocuments()
                || processingPollAttempts >= PROCESSING_POLL_LIMIT
            ) {
                stopProcessingPolling()
            }
        },
        PROCESSING_POLL_INTERVAL
    )
}


async function loadCollection() {
    loading.value = true
    clearMessages()

    try {
        collection.value = await getCollection(
            collectionId.value
        )

        if (currentUser.value) {
            addRecentCollection(
                currentUser.value.id,
                collection.value
            )
        }

        await refreshDocuments()
        startProcessingPolling()

        document.title = `${collection.value.name} — KnowledgeHub`
    }
    catch (error) {
        if (error.status === 404) {
            await router.replace({
                name: "collections"
            })

            return
        }

        showError(error.message)
    }
    finally {
        loading.value = false
    }
}


async function runSearch({
    updateUrl = true
} = {}) {
    const query = searchQuery.value.trim()

    if (!query) {
        showError(
            "Введіть пошуковий запит."
        )
        return
    }

    activeWorkspace.value = "search"
    searching.value = true
    clearMessages()

    try {
        const data = await searchCollection(
            collectionId.value,
            query,
            searchMode.value
        )

        searchResults.value = data.results || []
        searchActive.value = true

        if (updateUrl) {
            await router.replace({
                name: "collection-detail",
                params: {
                    collectionId: collectionId.value
                },
                query: {
                    q: query,
                    mode: searchMode.value
                }
            })
        }
    }
    catch (error) {
        showError(error.message)
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
            collectionId: collectionId.value
        }
    })
}


async function handleUploaded(
    uploadedCount = 1
) {
    clearMessages()

    const count =
        Number(
            uploadedCount
        ) || 1

    successMessage.value =
        count === 1
            ? (
                "Документ завантажено. "
                + "KnowledgeHub завершує його обробку."
            )
            : (
                `${count} документів завантажено. `
                + "KnowledgeHub завершує їх обробку."
            )

    await refreshDocuments()
    startProcessingPolling()
}


function handleCollectionSaved(updated) {
    clearMessages()

    collection.value = updated

    if (currentUser.value) {
        updateFavoriteCollection(
            currentUser.value.id,
            updated
        )

        updateRecentCollection(
            currentUser.value.id,
            updated
        )
    }

    successMessage.value =
        "Колекцію успішно оновлено."

    document.title = `${updated.name} — KnowledgeHub`
}


async function handleCollectionDeleted() {
    stopProcessingPolling()

    if (currentUser.value) {
        removeFavoriteCollection(
            currentUser.value.id,
            collectionId.value
        )

        removeRecentCollection(
            currentUser.value.id,
            collectionId.value
        )
    }

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


onMounted(
    async () => {
        await loadCollection()

        if (
            collection.value
            && searchQuery.value.trim()
        ) {
            activeWorkspace.value = "search"

            await runSearch({
                updateUrl: false
            })
        }
    }
)


onBeforeUnmount(
    stopProcessingPolling
)
</script>

<template>
    <section class="collections-page">
        <RouterLink
            class="page-back-button"
            :to="{ name: 'collections' }"
        >
            ← До колекцій
        </RouterLink>

        <AppBreadcrumbs
            :items="breadcrumbs"
        />

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

            <CollectionOverview
                :documents="documents"
            />

            <FeedbackMessages
                :errors="errors"
                :success-message="successMessage"
            />

            <nav
                class="collection-workspace-tabs"
                aria-label="Робоча область колекції"
            >
                <button
                    type="button"
                    :class="{
                        active: activeWorkspace === 'documents'
                    }"
                    @click="activeWorkspace = 'documents'"
                >
                    Документи
                    <span>{{ documents.length }}</span>
                </button>

                <button
                    type="button"
                    :class="{
                        active: activeWorkspace === 'search'
                    }"
                    @click="activeWorkspace = 'search'"
                >
                    Пошук
                </button>

                <button
                    type="button"
                    :class="{
                        active: activeWorkspace === 'research'
                    }"
                    @click="activeWorkspace = 'research'"
                >
                    Дослідження
                </button>
            </nav>

            <section
                v-if="activeWorkspace === 'documents'"
                class="collection-workspace-panel"
            >
                <DocumentsList
                    :collection-id="collectionId"
                    :collection-name="collection.name"
                    :documents="documents"
                    :search-active="false"
                    :score-map="{}"
                    :snippet-map="{}"
                    search-query=""
                    :search-mode="searchMode"
                    @upload="uploadDialog?.open()"
                />
            </section>

            <section
                v-else-if="activeWorkspace === 'search'"
                class="collection-workspace-panel"
            >
                <DocumentSearchPanel
                    v-model:mode="searchMode"
                    v-model:query="searchQuery"
                    :searching="searching"
                    :active="searchActive"
                    :result-count="visibleDocuments.length"
                    @search="runSearch()"
                    @clear="clearSearch"
                />

                <DocumentsList
                    v-if="searchActive"
                    :collection-id="collectionId"
                    :collection-name="collection.name"
                    :documents="visibleDocuments"
                    :search-active="true"
                    :score-map="scoreMap"
                    :snippet-map="snippetMap"
                    :search-query="searchQuery"
                    :search-mode="searchMode"
                    @upload="uploadDialog?.open()"
                />

                <div
                    v-else
                    class="collection-workspace-placeholder"
                >
                    <h3>
                        Знайдіть потрібні матеріали
                    </h3>

                    <p>
                        Введіть запит, оберіть режим пошуку
                        та натисніть «Знайти».
                    </p>
                </div>
            </section>

            <section
                v-else
                class="collection-workspace-panel"
            >
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
                            У поточному хмарному профілі
                            ресурсомісткі ML/LLM-функції
                            недоступні. Повна локальна
                            конфігурація KnowledgeHub
                            підтримує розширені
                            інтелектуальні режими.
                        </p>
                    </div>
                </section>
            </section>

            <DocumentUploadDialog
                ref="uploadDialog"
                :collection-id="collectionId"
                :existing-documents="documents"
                @opened="clearMessages"
                @uploaded="handleUploaded"
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

<style scoped>
.collection-workspace-tabs {
    display: inline-flex;
    max-width: 100%;
    gap: 5px;
    margin: 6px 0 20px;
    padding: 5px;
    overflow-x: auto;

    border: 1px solid var(--mezha);
    border-radius: 12px;
    background: var(--poverkhna);
}

.collection-workspace-tabs button {
    display: inline-flex;
    min-height: 42px;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 0 16px;

    border: 0;
    border-radius: 8px;
    background: transparent;
    color: var(--tekst-drugoryadnyi);

    font: inherit;
    font-size: 14px;
    font-weight: 700;
    white-space: nowrap;
    cursor: pointer;
}

.collection-workspace-tabs button:hover {
    background: var(--poverkhna-svitla);
}

.collection-workspace-tabs button.active {
    background: var(--poverkhna-svitla);
    color: var(--morskyi-hlybokyi);
    box-shadow: 0 1px 4px rgba(38, 60, 67, 0.08);
}

.collection-workspace-tabs span {
    display: inline-flex;
    min-width: 22px;
    height: 22px;
    align-items: center;
    justify-content: center;

    border-radius: 999px;
    background: var(--morska-pina);
    font-size: 11px;
}

.collection-workspace-panel {
    min-width: 0;
}

.collection-workspace-placeholder {
    padding: 34px;
    text-align: center;

    border: 1px dashed var(--mezha-temna);
    border-radius: 12px;
    background: var(--poverkhna-svitla);
}

.collection-workspace-placeholder h3 {
    margin-top: 0;
}

.collection-workspace-placeholder p {
    margin-bottom: 0;
    color: var(--tekst-drugoryadnyi);
}
</style>
