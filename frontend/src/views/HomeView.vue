<script setup>
import {
    computed,
    onMounted,
    ref,
    watch
} from "vue"

import {
    useAuth
} from "../composables/useAuth.js"

import {
    extractLocalDocumentText
} from "../utils/localDocumentText.js"

import {
    getRecentItems
} from "../utils/recentItems.js"


const {
    currentUser
} = useAuth()


const selectedFile = ref(null)
const selectedFileType = ref("")
const fileText = ref("")

const searchQuery = ref("")
const searchError = ref("")
const fileProcessing = ref(false)

const searched = ref(false)
const totalMatches = ref(0)
const resultSnippets = ref([])

const recentItems = ref([])


function loadRecentItems() {
    recentItems.value =
        currentUser.value
            ? getRecentItems()
            : []
}


onMounted(
    loadRecentItems
)

watch(
    currentUser,
    loadRecentItems
)


const selectedFileLabel = computed(
    () => {
        if (!selectedFile.value) {
            return "Р¤Р°Р№Р» РЅРµ РІРёР±СЂР°РЅРѕ"
        }

        const typeSuffix =
            selectedFileType.value
                ? ` (${selectedFileType.value})`
                : ""

        return (
            selectedFile.value.name
            + typeSuffix
        )
    }
)


const searchDisabled = computed(
    () =>
        fileProcessing.value
        || !selectedFile.value
)


function normalizeText(
    value
) {
    return value
        .replace(/\s+/g, " ")
        .trim()
}


function clearResults() {
    searchError.value = ""
    searched.value = false
    totalMatches.value = 0
    resultSnippets.value = []
}


async function handleFileSelection(
    event
) {
    clearResults()

    const file =
        event.target.files?.[0]
        ?? null

    selectedFile.value = null
    selectedFileType.value = ""
    fileText.value = ""

    if (!file) {
        return
    }

    const lowerName =
        file.name.toLowerCase()

    const supported =
        lowerName.endsWith(".txt")
        || lowerName.endsWith(".pdf")
        || lowerName.endsWith(".docx")

    if (!supported) {
        searchError.value =
            "РџС–РґС‚СЂРёРјСѓСЋС‚СЊСЃСЏ Р»РёС€Рµ TXT, PDF С– DOCX."

        event.target.value = ""
        return
    }

    const maxBytes =
        10 * 1024 * 1024

    if (file.size > maxBytes) {
        searchError.value =
            "Р¤Р°Р№Р» Р·Р°РІРµР»РёРєРёР№. "
            + "РњР°РєСЃРёРјР°Р»СЊРЅРёР№ СЂРѕР·РјС–СЂ вЂ” 10 РњР‘."

        event.target.value = ""
        return
    }

    fileProcessing.value = true

    try {
        const result =
            await extractLocalDocumentText(
                file
            )

        const text =
            result.text

        if (!text.trim()) {
            if (result.type === "PDF") {
                searchError.value =
                    "РЈ PDF РЅРµ РІРґР°Р»РѕСЃСЏ Р·РЅР°Р№С‚Рё С‚РµРєСЃС‚. "
                    + "РњРѕР¶Р»РёРІРѕ, С†Рµ СЃРєР°РЅРѕРІР°РЅС– СЃС‚РѕСЂС–РЅРєРё. "
                    + "OCR Сѓ РіРѕСЃС‚СЊРѕРІРѕРјСѓ СЂРµР¶РёРјС– РїРѕРєРё "
                    + "РЅРµ РїС–РґС‚СЂРёРјСѓС”С‚СЊСЃСЏ."
            }
            else {
                searchError.value =
                    "Р¤Р°Р№Р» РЅРµ РјС–СЃС‚РёС‚СЊ С‚РµРєСЃС‚Сѓ."
            }

            event.target.value = ""
            return
        }

        selectedFile.value = file
        selectedFileType.value =
            result.type

        fileText.value = text
    }
    catch (error) {
        console.error(
            "Local document parsing failed:",
            error
        )

        if (
            lowerName.endsWith(".pdf")
        ) {
            searchError.value =
                "РќРµ РІРґР°Р»РѕСЃСЏ РїСЂРѕС‡РёС‚Р°С‚Рё PDF. "
                + "Р¤Р°Р№Р» РјРѕР¶Рµ Р±СѓС‚Рё РїРѕС€РєРѕРґР¶РµРЅРёР№, "
                + "Р·Р°С…РёС‰РµРЅРёР№ РїР°СЂРѕР»РµРј Р°Р±Рѕ РјР°С‚Рё "
                + "РЅРµРїС–РґС‚СЂРёРјСѓРІР°РЅСѓ СЃС‚СЂСѓРєС‚СѓСЂСѓ."
        }
        else if (
            lowerName.endsWith(".docx")
        ) {
            searchError.value =
                "РќРµ РІРґР°Р»РѕСЃСЏ РїСЂРѕС‡РёС‚Р°С‚Рё DOCX. "
                + "РџРµСЂРµРІС–СЂС‚Рµ, С‰Рѕ С†Рµ РєРѕСЂРµРєС‚РЅРёР№ "
                + "РґРѕРєСѓРјРµРЅС‚ Microsoft Word."
        }
        else {
            searchError.value =
                "РќРµ РІРґР°Р»РѕСЃСЏ РїСЂРѕС‡РёС‚Р°С‚Рё Р»РѕРєР°Р»СЊРЅРёР№ С„Р°Р№Р»."
        }

        event.target.value = ""
    }
    finally {
        fileProcessing.value = false
    }
}


function runLocalSearch() {
    clearResults()

    const query =
        normalizeText(
            searchQuery.value
        )

    if (!selectedFile.value) {
        searchError.value =
            "РЎРїРѕС‡Р°С‚РєСѓ РІРёР±РµСЂС–С‚СЊ TXT, PDF Р°Р±Рѕ DOCX."
        return
    }

    if (!query) {
        searchError.value =
            "Р’РІРµРґС–С‚СЊ СЃР»РѕРІРѕ Р°Р±Рѕ С„СЂР°Р·Сѓ РґР»СЏ РїРѕС€СѓРєСѓ."
        return
    }

    const source =
        fileText.value

    const sourceLower =
        source.toLocaleLowerCase(
            "uk-UA"
        )

    const queryLower =
        query.toLocaleLowerCase(
            "uk-UA"
        )

    const snippets = []

    let cursor = 0
    let count = 0

    const snippetRadius = 90
    const maxSnippets = 12

    while (cursor < source.length) {
        const index =
            sourceLower.indexOf(
                queryLower,
                cursor
            )

        if (index === -1) {
            break
        }

        count += 1

        if (
            snippets.length
            < maxSnippets
        ) {
            const start =
                Math.max(
                    0,
                    index - snippetRadius
                )

            const end =
                Math.min(
                    source.length,
                    index
                    + query.length
                    + snippetRadius
                )

            let snippet =
                normalizeText(
                    source.slice(
                        start,
                        end
                    )
                )

            if (start > 0) {
                snippet =
                    "вЂ¦ " + snippet
            }

            if (end < source.length) {
                snippet += " вЂ¦"
            }

            snippets.push({
                number: count,
                text: snippet
            })
        }

        cursor =
            index
            + Math.max(
                1,
                query.length
            )
    }

    totalMatches.value = count
    resultSnippets.value = snippets
    searched.value = true
}


function resetLocalSearch() {
    selectedFile.value = null
    selectedFileType.value = ""
    fileText.value = ""

    searchQuery.value = ""
    searchError.value = ""
    fileProcessing.value = false

    searched.value = false
    totalMatches.value = 0
    resultSnippets.value = []

    const input =
        document.getElementById(
            "guest-file-input"
        )

    if (input) {
        input.value = ""
    }
}
</script>


<template>
    <section class="hero">
        <div class="hero-content">
            <p class="eyebrow">
                PERSONAL KNOWLEDGE PLATFORM
            </p>

            <h1>
                РћСЂРіР°РЅС–Р·РѕРІСѓР№С‚Рµ СЃРІРѕС— Р·РЅР°РЅРЅСЏ РІ РѕРґРЅРѕРјСѓ РјС–СЃС†С–
            </h1>

            <p class="hero-description">
                KnowledgeHub вЂ” РїР»Р°С‚С„РѕСЂРјР° РґР»СЏ СЃС‚РІРѕСЂРµРЅРЅСЏ РєРѕР»РµРєС†С–Р№,
                Р·Р±РµСЂС–РіР°РЅРЅСЏ РґРѕРєСѓРјРµРЅС‚С–РІ, РїРѕС€СѓРєСѓ С–РЅС„РѕСЂРјР°С†С–С— С‚Р°
                РїРѕРґР°Р»СЊС€РѕРіРѕ С–РЅС‚РµР»РµРєС‚СѓР°Р»СЊРЅРѕРіРѕ Р°РЅР°Р»С–Р·Сѓ РјР°С‚РµСЂС–Р°Р»С–РІ.
            </p>

            <div class="hero-actions">
                <RouterLink
                    v-if="currentUser"
                    class="button primary"
                    :to="{ name: 'collections' }"
                >
                    Р’С–РґРєСЂРёС‚Рё РјРѕС— РєРѕР»РµРєС†С–С—
                </RouterLink>

                <template v-else>
                    <RouterLink
                        class="button primary"
                        :to="{ name: 'register' }"
                    >
                        РЎС‚РІРѕСЂРёС‚Рё Р°РєР°СѓРЅС‚
                    </RouterLink>

                    <RouterLink
                        class="button secondary-home"
                        :to="{ name: 'login' }"
                    >
                        РЈРІС–Р№С‚Рё
                    </RouterLink>
                </template>

                <RouterLink
                    class="button secondary-home"
                    :to="{ name: 'about' }"
                >
                    РџСЂРѕ СЃРёСЃС‚РµРјСѓ
                </RouterLink>
            </div>
        </div>
    </section>

    <section
        class="guest-search"
        aria-labelledby="guest-search-title"
    >
        <div class="guest-search-intro">
            <p class="eyebrow">
                QUICK LOCAL SEARCH
            </p>

            <h2 id="guest-search-title">
                РЁРІРёРґРєРёР№ РїРѕС€СѓРє Сѓ Р»РѕРєР°Р»СЊРЅРѕРјСѓ С„Р°Р№Р»С–
            </h2>

            <p>
                Р’РёР±РµСЂС–С‚СЊ TXT, PDF Р°Р±Рѕ DOCX
                С– Р·РЅР°Р№РґС–С‚СЊ РїРѕС‚СЂС–Р±РЅРµ СЃР»РѕРІРѕ
                С‡Рё С„СЂР°Р·Сѓ Р±РµР· СЂРµС”СЃС‚СЂР°С†С–С—.
            </p>

            <p class="guest-search-privacy">
                Р¤Р°Р№Р» РѕР±СЂРѕР±Р»СЏС”С‚СЊСЃСЏ С‚С–Р»СЊРєРё Сѓ РІР°С€РѕРјСѓ Р±СЂР°СѓР·РµСЂС–:
                РІС–РЅ РЅРµ Р·Р°РІР°РЅС‚Р°Р¶СѓС”С‚СЊСЃСЏ РЅР° СЃРµСЂРІРµСЂ KnowledgeHub
                С– РЅРµ Р·Р±РµСЂС–РіР°С”С‚СЊСЃСЏ РІ Р±Р°Р·С– РґР°РЅРёС….
            </p>

            <p class="guest-search-privacy">
                Р”Р»СЏ PDF РІРёРєРѕРЅСѓС”С‚СЊСЃСЏ РїРѕС€СѓРє Сѓ С‚РµРєСЃС‚РѕРІРѕРјСѓ С€Р°СЂС–.
                РЎРєР°РЅРѕРІР°РЅС– PDF Р±РµР· С‚РµРєСЃС‚РѕРІРѕРіРѕ С€Р°СЂСѓ РїРѕС‚СЂРµР±СѓСЋС‚СЊ OCR
                С– РїРѕРєРё РЅРµ РїС–РґС‚СЂРёРјСѓСЋС‚СЊСЃСЏ РІ РіРѕСЃС‚СЊРѕРІРѕРјСѓ СЂРµР¶РёРјС–.
            </p>
        </div>

        <div class="guest-search-panel">
            <div class="guest-file-field">
                <label
                    class="guest-file-label"
                    for="guest-file-input"
                >
                    Р’РёР±СЂР°С‚Рё С„Р°Р№Р»
                </label>

                <input
                    id="guest-file-input"
                    class="guest-file-input"
                    type="file"
                    accept="
                        .txt,
                        text/plain,
                        .pdf,
                        application/pdf,
                        .docx,
                        application/vnd.openxmlformats-officedocument.wordprocessingml.document
                    "
                    @change="handleFileSelection"
                >

                <span class="guest-file-name">
                    {{
                        fileProcessing
                            ? "РћР±СЂРѕР±РєР° РґРѕРєСѓРјРµРЅС‚Р°..."
                            : selectedFileLabel
                    }}
                </span>
            </div>

            <form
                class="guest-search-form"
                @submit.prevent="runLocalSearch"
            >
                <label for="guest-search-query">
                    РЎР»РѕРІРѕ Р°Р±Рѕ С„СЂР°Р·Р°
                </label>

                <div class="guest-search-row">
                    <input
                        id="guest-search-query"
                        v-model="searchQuery"
                        type="search"
                        maxlength="120"
                        autocomplete="off"
                        placeholder="РќР°РїСЂРёРєР»Р°Рґ: РїСЂРѕРґСѓРєС‚РёРІРЅС–СЃС‚СЊ"
                    >

                    <button
                        class="guest-search-submit"
                        type="submit"
                        :disabled="searchDisabled"
                    >
                        {{
                            fileProcessing
                                ? "РћР±СЂРѕР±РєР°..."
                                : "Р—РЅР°Р№С‚Рё"
                        }}
                    </button>

                    <button
                        class="guest-search-reset"
                        type="button"
                        :disabled="fileProcessing"
                        @click="resetLocalSearch"
                    >
                        РћС‡РёСЃС‚РёС‚Рё
                    </button>
                </div>
            </form>

            <div
                v-if="searchError"
                class="message message-error"
            >
                {{ searchError }}
            </div>

            <div
                v-if="searched"
                class="guest-search-results"
                aria-live="polite"
            >
                <div class="guest-search-summary">
                    <strong>
                        Р—РЅР°Р№РґРµРЅРѕ Р·Р±С–РіС–РІ:
                        {{ totalMatches }}
                    </strong>

                    <span
                        v-if="
                            totalMatches
                            > resultSnippets.length
                        "
                    >
                        РџРѕРєР°Р·Р°РЅРѕ РїРµСЂС€С–
                        {{ resultSnippets.length }}
                        С„СЂР°РіРјРµРЅС‚С–РІ.
                    </span>
                </div>

                <ol
                    v-if="resultSnippets.length"
                    class="guest-snippet-list"
                >
                    <li
                        v-for="snippet in resultSnippets"
                        :key="snippet.number"
                    >
                        {{ snippet.text }}
                    </li>
                </ol>

                <p
                    v-else
                    class="guest-search-empty"
                >
                    РЈ РІРёР±СЂР°РЅРѕРјСѓ С„Р°Р№Р»С– Р·Р±С–РіС–РІ РЅРµ Р·РЅР°Р№РґРµРЅРѕ.
                </p>
            </div>
        </div>
    </section>

    <section
        v-if="currentUser && recentItems.length"
        class="recent-section"
        aria-labelledby="recent-title"
    >
        <div class="recent-heading">
            <div>
                <p class="eyebrow">
                    RECENT
                </p>

                <h2 id="recent-title">
                    Нещодавні
                </h2>

                <p>
                    Швидкий доступ до останніх
                    відкритих матеріалів.
                </p>
            </div>

            <RouterLink
                class="recent-all-link"
                :to="{ name: 'collections' }"
            >
                Усі колекції →
            </RouterLink>
        </div>

        <div class="recent-grid">
            <RouterLink
                v-for="item in recentItems"
                :key="
                    item.type
                    + '-'
                    + item.collectionId
                    + '-'
                    + item.id
                "
                class="recent-card"
                :to="
                    item.type === 'document'
                        ? {
                            name: 'document',
                            params: {
                                collectionId:
                                    item.collectionId,
                                documentId:
                                    item.id
                            }
                        }
                        : {
                            name: 'collection-detail',
                            params: {
                                collectionId:
                                    item.collectionId
                            }
                        }
                "
            >
                <span class="recent-type">
                    {{
                        item.type === "document"
                            ? "ДОКУМЕНТ"
                            : "КОЛЕКЦІЯ"
                    }}
                </span>

                <strong>
                    {{ item.name }}
                </strong>

                <span class="recent-open">
                    Відкрити →
                </span>
            </RouterLink>
        </div>
    </section>
    <section class="features">
        <article class="feature-card">
            <h2>РљРѕР»РµРєС†С–С—</h2>

            <p>
                РћР±'С”РґРЅСѓР№С‚Рµ РґРѕРєСѓРјРµРЅС‚Рё Р·Р° С‚РµРјР°РјРё,
                РїСЂРѕС”РєС‚Р°РјРё Р°Р±Рѕ РЅР°РїСЂСЏРјР°РјРё РґРѕСЃР»С–РґР¶РµРЅРЅСЏ.
            </p>
        </article>

        <article class="feature-card">
            <h2>Р”РѕРєСѓРјРµРЅС‚Рё</h2>

            <p>
                Р—Р±РµСЂС–РіР°Р№С‚Рµ РІР»Р°СЃРЅСѓ СЃС‚СЂСѓРєС‚СѓСЂРѕРІР°РЅСѓ
                Р±Р°Р·Сѓ РјР°С‚РµСЂС–Р°Р»С–РІ.
            </p>
        </article>

        <article class="feature-card">
            <h2>РџРѕС€СѓРє</h2>

            <p>
                Р’РёРєРѕСЂРёСЃС‚РѕРІСѓР№С‚Рµ lexical, semantic
                С– hybrid РїРѕС€СѓРє Сѓ РІР»Р°СЃРЅРёС… РєРѕР»РµРєС†С–СЏС….
            </p>
        </article>
    </section>
</template>
