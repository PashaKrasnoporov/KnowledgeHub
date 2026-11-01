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
        <header class="guest-search-heading">
            <div>
                <p class="eyebrow">
                    QUICK LOCAL SEARCH
                </p>

                <h2 id="guest-search-title">
                    Швидкий пошук у локальному файлі
                </h2>

                <p>
                    Знайдіть потрібне слово або фразу
                    у TXT, PDF чи DOCX без завантаження
                    документа на сервер.
                </p>
            </div>

            <div class="guest-search-heading-badges">
                <span>
                    TXT
                </span>

                <span>
                    PDF
                </span>

                <span>
                    DOCX
                </span>

                <span>
                    ≤ 10 МБ
                </span>
            </div>
        </header>

        <div class="guest-search-layout">
            <div class="guest-search-workspace">
                <div class="guest-search-step">
                    <div class="guest-step-heading">
                        <span class="guest-step-number">
                            1
                        </span>

                        <div>
                            <strong>
                                Оберіть документ
                            </strong>

                            <span>
                                Файл буде прочитано
                                безпосередньо у браузері.
                            </span>
                        </div>
                    </div>

                    <label
                        class="guest-file-dropzone"
                        for="guest-file-input"
                    >
                        <span class="guest-file-icon">
                            ↑
                        </span>

                        <span class="guest-file-copy">
                            <strong>
                                {{
                                    fileProcessing
                                        ? "Обробка документа..."
                                        : (
                                            selectedFile
                                                ? selectedFile.name
                                                : "Виберіть локальний файл"
                                        )
                                }}
                            </strong>

                            <small>
                                {{
                                    selectedFile
                                        ? selectedFileLabel
                                        : "TXT, PDF або DOCX · максимум 10 МБ"
                                }}
                            </small>
                        </span>

                        <span class="guest-file-action">
                            {{
                                selectedFile
                                    ? "Змінити"
                                    : "Вибрати файл"
                            }}
                        </span>
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
                </div>

                <form
                    class="guest-search-form"
                    @submit.prevent="runLocalSearch"
                >
                    <div class="guest-step-heading">
                        <span class="guest-step-number">
                            2
                        </span>

                        <div>
                            <strong>
                                Введіть слово або фразу
                            </strong>

                            <span>
                                Пошук не змінює
                                і не зберігає файл.
                            </span>
                        </div>
                    </div>

                    <div class="guest-search-row">
                        <input
                            id="guest-search-query"
                            v-model="searchQuery"
                            type="search"
                            maxlength="120"
                            autocomplete="off"
                            aria-label="Слово або фраза"
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
                        У вибраному файлі
                        збігів не знайдено.
                    </p>
                </div>
            </div>

            <aside class="guest-search-aside">
                <div>
                    <p class="eyebrow">
                        LOCAL & PRIVATE
                    </p>

                    <h3>
                        Ваш документ залишається у вас
                    </h3>

                    <p>
                        Quick Local Search працює
                        повністю на стороні браузера.
                        Файл не потрапляє до колекцій,
                        бази даних або серверного сховища.
                    </p>
                </div>

                <div class="guest-search-facts">
                    <div>
                        <strong>
                            TXT · PDF · DOCX
                        </strong>

                        <span>
                            підтримувані формати
                        </span>
                    </div>

                    <div>
                        <strong>
                            до 10 МБ
                        </strong>

                        <span>
                            максимальний розмір
                        </span>
                    </div>

                    <div>
                        <strong>
                            Локально
                        </strong>

                        <span>
                            без передачі на сервер
                        </span>
                    </div>
                </div>

                <div class="guest-search-note">
                    <strong>
                        Що з PDF-сканами?
                    </strong>

                    <p>
                        Пошук працює по текстовому шару PDF.
                        Якщо документ складається лише
                        зі сканованих зображень,
                        потрібен OCR — він поки
                        не підтримується у цьому режимі.
                    </p>
                </div>

                <RouterLink
                    class="guest-search-about"
                    :to="{ name: 'about' }"
                >
                    Дізнатися більше про KnowledgeHub →
                </RouterLink>
            </aside>
        </div>
    </section>

    <FavoriteItems
        v-if="currentUser"
        :user-id="currentUser.id"
    />

    <RecentItems
        v-if="currentUser"
        :user-id="currentUser.id"
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
