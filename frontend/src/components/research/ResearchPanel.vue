<script setup>
import {
    onBeforeUnmount,
    ref,
    watch
} from "vue"

import {
    generateResearchAnswer,
    researchCollection
} from "../../api/index.js"

import ResearchAnswer from "./ResearchAnswer.vue"
import ResearchLoading from "./ResearchLoading.vue"
import ResearchSources from "./ResearchSources.vue"

const props = defineProps({
    collectionId: {
        type: Number,
        required: true
    }
})

const question = ref(
    localStorage.getItem(
        "knowledgehub.researchQuestion"
    ) || ""
)

const generationMode = ref(
    localStorage.getItem(
        "knowledgehub.researchGenerationMode"
    ) || "extractive"
)

const responseLanguage = ref(
    localStorage.getItem(
        "knowledgehub.researchLanguage"
    ) || "uk"
)

const loading = ref(false)
const elapsedSeconds = ref(0)
const error = ref("")
const result = ref(null)

let elapsedTimer = null

watch(
    question,
    value => {
        localStorage.setItem(
            "knowledgehub.researchQuestion",
            value
        )
    }
)

watch(
    generationMode,
    value => {
        localStorage.setItem(
            "knowledgehub.researchGenerationMode",
            value
        )
    }
)

watch(
    responseLanguage,
    value => {
        localStorage.setItem(
            "knowledgehub.researchLanguage",
            value
        )
    }
)

function startLoadingTimer() {
    stopLoadingTimer()

    elapsedSeconds.value = 0

    elapsedTimer = window.setInterval(
        () => {
            elapsedSeconds.value += 1
        },
        1000
    )
}

function stopLoadingTimer() {
    if (elapsedTimer !== null) {
        window.clearInterval(
            elapsedTimer
        )

        elapsedTimer = null
    }
}

async function runResearch() {
    if (loading.value) {
        return
    }

    const normalized =
        question.value.trim()

    if (normalized.length < 3) {
        error.value =
            "Введіть запитання щонайменше з 3 символів."

        return
    }

    loading.value = true
    error.value = ""
    result.value = null

    startLoadingTimer()

    try {
        if (
            generationMode.value
            === "local"
        ) {
            result.value =
                await generateResearchAnswer(
                    props.collectionId,
                    normalized,
                    5,
                    responseLanguage.value
                )
        }
        else {
            result.value =
                await researchCollection(
                    props.collectionId,
                    normalized,
                    5
                )
        }
    }
    catch (requestError) {
        error.value =
            requestError.message
            || "Не вдалося сформувати дослідницьку відповідь."
    }
    finally {
        loading.value = false
        stopLoadingTimer()
    }
}

function clearResearch() {
    result.value = null
    error.value = ""
    question.value = ""
}

onBeforeUnmount(
    () => {
        stopLoadingTimer()
    }
)
</script>

<template>
    <section class="research-panel">
        <div class="research-heading">
            <div>
                <div class="research-title-row">
                    <h2>
                        Дослідницька відповідь
                    </h2>

                    <span class="research-badge">
                        RAG v1.2
                    </span>

                    <span class="research-language-badge">
                        Українська — пріоритет
                    </span>
                </div>

                <p>
                    KnowledgeHub знаходить докази
                    у документах, формує відповідь
                    і автоматично перевіряє кожне
                    твердження. Українська мова
                    використовується за замовчуванням.
                </p>
            </div>

            <span
                class="info-tooltip"
                tabindex="0"
                aria-label="Як працює RAG"
            >
                <span class="info-icon">
                    i
                </span>

                <span class="tooltip-content">
                    <strong>
                        RAG v1.2
                    </strong>

                    <span>
                        Retrieval знаходить докази
                        на рівні document chunks.
                    </span>

                    <span>
                        LLM генерує текст,
                        а KnowledgeHub окремо
                        перевіряє твердження.
                    </span>

                    <span>
                        Якщо evidence слабке,
                        система не запускає
                        генерацію і не вигадує відповідь.
                    </span>
                </span>
            </span>
        </div>

        <form
            class="research-form"
            @submit.prevent="runResearch"
        >
            <div class="research-settings-grid">
                <div>
                    <label
                        class="document-search-label"
                        for="research-mode"
                    >
                        Режим відповіді
                    </label>

                    <select
                        id="research-mode"
                        v-model="generationMode"
                        class="search-mode-select"
                        :disabled="loading"
                    >
                        <option value="extractive">
                            Швидка чернетка
                        </option>

                        <option value="local">
                            Локальна LLM
                        </option>
                    </select>
                </div>

                <div
                    v-if="generationMode === 'local'"
                >
                    <label
                        class="document-search-label"
                        for="research-language"
                    >
                        Мова відповіді
                    </label>

                    <select
                        id="research-language"
                        v-model="responseLanguage"
                        class="search-mode-select"
                        :disabled="loading"
                    >
                        <option value="uk">
                            Українська
                        </option>

                        <option value="auto">
                            Автоматично
                        </option>
                    </select>
                </div>

                <p class="research-local-note">
                    {{
                        generationMode === "local"
                            ? (
                                responseLanguage === "uk"
                                    ? "Модель повинна відповідати нормативною українською; за потреби система виконує мовну нормалізацію."
                                    : "Мова визначається за формулюванням запитання."
                            )
                            : "Швидкий режим без генеративної моделі."
                    }}
                </p>
            </div>

            <div class="research-question-heading">
                <label
                    class="document-search-label"
                    for="research-question"
                >
                    Запитання
                </label>

                <span>
                    {{ question.length }}/500
                </span>
            </div>

            <div class="research-input-row">
                <textarea
                    id="research-question"
                    v-model="question"
                    rows="3"
                    maxlength="500"
                    :disabled="loading"
                    placeholder="Наприклад: Як у документах пояснюється роль embeddings у RAG?"
                    @keydown.ctrl.enter.prevent="runResearch"
                ></textarea>

                <button
                    class="document-search-button research-submit-button"
                    type="submit"
                    :disabled="loading"
                >
                    <span
                        v-if="loading"
                        class="research-button-spinner"
                        aria-hidden="true"
                    ></span>

                    {{
                        loading
                            ? (
                                generationMode === "local"
                                    ? "Генерація..."
                                    : "Аналіз..."
                            )
                            : "Сформувати"
                    }}
                </button>
            </div>

            <div class="research-form-hint">
                <span>
                    Ctrl + Enter — сформувати
                </span>

                <span
                    v-if="generationMode === 'local'"
                >
                    Відповідь перевіряється
                    на рівні окремих тверджень.
                </span>
            </div>
        </form>

        <ResearchLoading
            v-if="loading"
            :elapsed-seconds="elapsedSeconds"
            :local-mode="
                generationMode === 'local'
            "
        />

        <div
            v-if="error"
            class="research-error"
        >
            {{ error }}
        </div>

        <template v-if="result">
            <div
                v-if="
                    result.sources.length
                    || result.generated_answer
                "
                class="research-result"
            >
                <ResearchAnswer
                    :result="result"
                    :generation-mode="generationMode"
                    @clear="clearResearch"
                />

                <ResearchSources
                    v-if="result.sources.length"
                    :collection-id="collectionId"
                    :sources="result.sources"
                />
            </div>

            <div
                v-else
                class="research-empty"
            >
                <h3>
                    Доказів не знайдено
                </h3>

                <p>
                    Для цього запитання в поточній
                    колекції не знайдено достатньо
                    релевантних фрагментів.
                </p>
            </div>
        </template>
    </section>
</template>
