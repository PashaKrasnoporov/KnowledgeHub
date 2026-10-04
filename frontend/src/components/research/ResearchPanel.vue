<script setup>
import {
    ref,
    watch
} from "vue"

import {
    generateResearchAnswer,
    researchCollection
} from "../../api/index.js"

import ResearchAnswer from "./ResearchAnswer.vue"
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

const loading = ref(false)
const error = ref("")
const result = ref(null)

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

async function runResearch() {
    const normalized =
        question.value.trim()

    if (normalized.length < 3) {
        error.value =
            "Введіть запитання щонайменше з 3 символів."

        return
    }

    loading.value = true
    error.value = ""

    try {
        if (
            generationMode.value
            === "local"
        ) {
            result.value =
                await generateResearchAnswer(
                    props.collectionId,
                    normalized,
                    5
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
    }
}

function clearResearch() {
    result.value = null
    error.value = ""
    question.value = ""
}
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
                        RAG v1.1
                    </span>
                </div>

                <p>
                    KnowledgeHub знаходить релевантні
                    фрагменти документів. У режимі
                    локальної LLM модель формує текст,
                    а система сама перевіряє кожне
                    твердження і прив'язує його
                    до найближчого джерела.
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
                        RAG v1.1
                    </strong>

                    <span>
                        Retrieval знаходить докази
                        на рівні document chunks.
                    </span>

                    <span>
                        LLM більше не відповідає
                        за citations. Вона генерує
                        лише змістовний текст.
                    </span>

                    <span>
                        KnowledgeHub окремо порівнює
                        кожне твердження з джерелами
                        за embeddings і lexical overlap,
                        після чого сам додає [1], [2]...
                    </span>
                </span>
            </span>
        </div>

        <form
            class="research-form"
            @submit.prevent="runResearch"
        >
            <div class="research-mode-row">
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
                    >
                        <option value="extractive">
                            Швидка чернетка
                        </option>

                        <option value="local">
                            Локальна LLM
                        </option>
                    </select>
                </div>

                <p
                    v-if="generationMode === 'local'"
                    class="research-local-note"
                >
                    LLM формує текст без citations.
                    KnowledgeHub автоматично перевіряє
                    твердження і додає джерела.
                </p>

                <p
                    v-else
                    class="research-local-note"
                >
                    Працює без генеративної моделі:
                    швидко відбирає релевантні речення
                    з джерел.
                </p>
            </div>

            <label
                class="document-search-label"
                for="research-question"
            >
                Запитання
            </label>

            <div class="research-input-row">
                <textarea
                    id="research-question"
                    v-model="question"
                    rows="3"
                    maxlength="500"
                    placeholder="Наприклад: Як у документах пояснюється роль embeddings у RAG?"
                ></textarea>

                <button
                    class="document-search-button"
                    type="submit"
                    :disabled="loading"
                >
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
        </form>

        <div
            v-if="error"
            class="research-error"
        >
            {{ error }}
        </div>

        <template v-if="result">
            <div
                v-if="result.sources.length"
                class="research-result"
            >
                <ResearchAnswer
                    :result="result"
                    :generation-mode="generationMode"
                    @clear="clearResearch"
                />

                <ResearchSources
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
