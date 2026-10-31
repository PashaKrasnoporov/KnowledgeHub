<script setup>
import {
    computed,
    ref
} from "vue"

import {
    useAuth
} from "../composables/useAuth.js"

import FavoriteItems from "../components/common/FavoriteItems.vue"
import RecentItems from "../components/common/RecentItems.vue"

import {
    extractLocalDocumentText
} from "../utils/localDocumentText.js"


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


const selectedFileLabel = computed(
    () => {
        if (!selectedFile.value) {
            return "Файл не вибрано"
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
            "Підтримуються лише TXT, PDF і DOCX."

        event.target.value = ""
        return
    }

    const maxBytes =
        10 * 1024 * 1024

    if (file.size > maxBytes) {
        searchError.value =
            "Файл завеликий. "
            + "Максимальний розмір — 10 МБ."

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
                    "У PDF не вдалося знайти текст. "
                    + "Можливо, це скановані сторінки. "
                    + "OCR у гостьовому режимі поки "
                    + "не підтримується."
            }
            else {
                searchError.value =
                    "Файл не містить тексту."
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
                "Не вдалося прочитати PDF. "
                + "Файл може бути пошкоджений, "
                + "захищений паролем або мати "
                + "непідтримувану структуру."
        }
        else if (
            lowerName.endsWith(".docx")
        ) {
            searchError.value =
                "Не вдалося прочитати DOCX. "
                + "Перевірте, що це коректний "
                + "документ Microsoft Word."
        }
        else {
            searchError.value =
                "Не вдалося прочитати локальний файл."
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
            "Спочатку виберіть TXT, PDF або DOCX."
        return
    }

    if (!query) {
        searchError.value =
            "Введіть слово або фразу для пошуку."
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
                    "… " + snippet
            }

            if (end < source.length) {
                snippet += " …"
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
                Організовуйте свої знання в одному місці
            </h1>

            <p class="hero-description">
                KnowledgeHub — платформа для створення колекцій,
                зберігання документів, пошуку інформації та
                подальшого інтелектуального аналізу матеріалів.
            </p>

            <div class="hero-actions">
                <RouterLink
                    v-if="currentUser"
                    class="button primary"
                    :to="{ name: 'collections' }"
                >
                    Відкрити мої колекції
                </RouterLink>

                <template v-else>
                    <RouterLink
                        class="button primary"
                        :to="{ name: 'register' }"
                    >
                        Створити акаунт
                    </RouterLink>

                    <RouterLink
                        class="button secondary-home"
                        :to="{ name: 'login' }"
                    >
                        Увійти
                    </RouterLink>
                </template>

                <RouterLink
                    class="button secondary-home"
                    :to="{ name: 'about' }"
                >
                    Про систему
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
                Швидкий пошук у локальному файлі
            </h2>

            <p>
                Виберіть TXT, PDF або DOCX
                і знайдіть потрібне слово
                чи фразу без реєстрації.
            </p>

            <p class="guest-search-privacy">
                Файл обробляється тільки у вашому браузері:
                він не завантажується на сервер KnowledgeHub
                і не зберігається в базі даних.
            </p>

            <p class="guest-search-privacy">
                Для PDF виконується пошук у текстовому шарі.
                Скановані PDF без текстового шару потребують OCR
                і поки не підтримуються в гостьовому режимі.
            </p>
        </div>

        <div class="guest-search-panel">
            <div class="guest-file-field">
                <label
                    class="guest-file-label"
                    for="guest-file-input"
                >
                    Вибрати файл
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
                            ? "Обробка документа..."
                            : selectedFileLabel
                    }}
                </span>
            </div>

            <form
                class="guest-search-form"
                @submit.prevent="runLocalSearch"
            >
                <label for="guest-search-query">
                    Слово або фраза
                </label>

                <div class="guest-search-row">
                    <input
                        id="guest-search-query"
                        v-model="searchQuery"
                        type="search"
                        maxlength="120"
                        autocomplete="off"
                        placeholder="Наприклад: продуктивність"
                    >

                    <button
                        class="guest-search-submit"
                        type="submit"
                        :disabled="searchDisabled"
                    >
                        {{
                            fileProcessing
                                ? "Обробка..."
                                : "Знайти"
                        }}
                    </button>

                    <button
                        class="guest-search-reset"
                        type="button"
                        :disabled="fileProcessing"
                        @click="resetLocalSearch"
                    >
                        Очистити
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
                        Знайдено збігів:
                        {{ totalMatches }}
                    </strong>

                    <span
                        v-if="
                            totalMatches
                            > resultSnippets.length
                        "
                    >
                        Показано перші
                        {{ resultSnippets.length }}
                        фрагментів.
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
                    У вибраному файлі збігів не знайдено.
                </p>
            </div>
        </div>
    </section>

    <FavoriteItems
        v-if="currentUser"
        :user-id="currentUser.id"
    />

    <RecentItems
        v-if="currentUser"
    />

    <section class="features">
        <article class="feature-card">
            <h2>Колекції</h2>

            <p>
                Об'єднуйте документи за темами,
                проєктами або напрямами дослідження.
            </p>
        </article>

        <article class="feature-card">
            <h2>Документи</h2>

            <p>
                Зберігайте власну структуровану
                базу матеріалів.
            </p>
        </article>

        <article class="feature-card">
            <h2>Пошук</h2>

            <p>
                Використовуйте lexical, semantic
                і hybrid пошук у власних колекціях.
            </p>
        </article>
    </section>
</template>
