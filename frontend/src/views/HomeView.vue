<script setup>
import {
    computed,
    ref
} from "vue"

import {
    useAuth
} from "../composables/useAuth.js"


const {
    currentUser
} = useAuth()


const selectedFile = ref(null)
const fileText = ref("")
const searchQuery = ref("")
const searchError = ref("")
const searched = ref(false)
const totalMatches = ref(0)
const resultSnippets = ref([])


const selectedFileLabel = computed(
    () => {
        if (!selectedFile.value) {
            return "Файл не вибрано"
        }

        return selectedFile.value.name
    }
)


function normalizeText(
    value
) {
    return value
        .replace(/\s+/g, " ")
        .trim()
}


async function handleFileSelection(
    event
) {
    searchError.value = ""
    searched.value = false
    totalMatches.value = 0
    resultSnippets.value = []

    const file =
        event.target.files?.[0] ?? null

    selectedFile.value = null
    fileText.value = ""

    if (!file) {
        return
    }

    const lowerName =
        file.name.toLowerCase()

    if (!lowerName.endsWith(".txt")) {
        searchError.value =
            "Для швидкого гостьового пошуку "
            + "поки підтримуються лише TXT-файли."

        event.target.value = ""
        return
    }

    const maxBytes =
        2 * 1024 * 1024

    if (file.size > maxBytes) {
        searchError.value =
            "Файл завеликий. "
            + "Максимальний розмір для демо — 2 МБ."

        event.target.value = ""
        return
    }

    try {
        const text =
            await file.text()

        if (!text.trim()) {
            searchError.value =
                "Файл не містить тексту."

            event.target.value = ""
            return
        }

        selectedFile.value = file
        fileText.value = text
    }
    catch {
        searchError.value =
            "Не вдалося прочитати локальний файл."

        event.target.value = ""
    }
}


function runLocalSearch() {
    searchError.value = ""
    searched.value = false
    totalMatches.value = 0
    resultSnippets.value = []

    const query =
        normalizeText(
            searchQuery.value
        )

    if (!selectedFile.value) {
        searchError.value =
            "Спочатку виберіть TXT-файл."
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
        source.toLocaleLowerCase("uk-UA")

    const queryLower =
        query.toLocaleLowerCase("uk-UA")

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

        if (snippets.length < maxSnippets) {
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
    fileText.value = ""
    searchQuery.value = ""
    searchError.value = ""
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
                Виберіть TXT-файл і знайдіть потрібне слово
                або фразу без реєстрації.
            </p>

            <p class="guest-search-privacy">
                Файл обробляється тільки у вашому браузері:
                він не завантажується на сервер KnowledgeHub
                і не зберігається в базі даних.
            </p>
        </div>

        <div class="guest-search-panel">
            <div class="guest-file-field">
                <label
                    class="guest-file-label"
                    for="guest-file-input"
                >
                    Вибрати TXT-файл
                </label>

                <input
                    id="guest-file-input"
                    class="guest-file-input"
                    type="file"
                    accept=".txt,text/plain"
                    @change="handleFileSelection"
                >

                <span class="guest-file-name">
                    {{ selectedFileLabel }}
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
                    >
                        Знайти
                    </button>

                    <button
                        class="guest-search-reset"
                        type="button"
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
                        v-if="totalMatches > resultSnippets.length"
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