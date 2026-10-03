<script setup>
import {
    ref,
    watch
} from "vue"

import {
    researchCollection
} from "../../api/index.js"

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
        result.value =
            await researchCollection(
                props.collectionId,
                normalized,
                5
            )
    }
    catch (requestError) {
        error.value =
            requestError.message
            || "Не вдалося сформувати дослідницький контекст."
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
                        RAG foundation
                    </span>
                </div>

                <p>
                    Поставте запитання до документів.
                    KnowledgeHub знайде найбільш релевантні
                    фрагменти та сформує доказову чернетку
                    з посиланнями на джерела.
                </p>
            </div>

            <span
                class="info-tooltip"
                tabindex="0"
                aria-label="Як працює дослідницький режим"
            >
                <span class="info-icon">
                    i
                </span>

                <span class="tooltip-content">
                    <strong>
                        Дослідницький режим
                    </strong>

                    <span>
                        Запит порівнюється з окремими
                        фрагментами документів за змістом
                        та ключовими словами.
                    </span>

                    <span>
                        Поточна версія формує
                        витягувальну чернетку без
                        зовнішньої генеративної моделі.
                    </span>
                </span>
            </span>
        </div>

        <form
            class="research-form"
            @submit.prevent="runResearch"
        >
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
                            ? "Аналіз..."
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
                <div class="research-answer">
                    <div class="research-result-heading">
                        <h3>
                            Чернетка відповіді
                        </h3>

                        <button
                            class="research-clear-button"
                            type="button"
                            @click="clearResearch"
                        >
                            Очистити
                        </button>
                    </div>

                    <ol
                        v-if="result.answer_points.length"
                        class="research-points"
                    >
                        <li
                            v-for="point in result.answer_points"
                            :key="
                                `${point.source_number}-${point.text}`
                            "
                        >
                            <span>
                                {{ point.text }}
                            </span>

                            <a
                                :href="
                                    `#research-source-${point.source_number}`
                                "
                            >
                                [{{ point.source_number }}]
                            </a>
                        </li>
                    </ol>

                    <p
                        v-else
                        class="research-empty-copy"
                    >
                        Релевантні фрагменти знайдено,
                        але коротку чернетку сформувати
                        не вдалося. Перегляньте джерела нижче.
                    </p>
                </div>

                <div class="research-sources">
                    <div class="research-result-heading">
                        <h3>
                            Джерела
                        </h3>

                        <span>
                            {{ result.count }} фрагм.
                        </span>
                    </div>

                    <article
                        v-for="source in result.sources"
                        :id="
                            `research-source-${source.source_number}`
                        "
                        :key="
                            `${source.document_id}-${source.chunk_index}`
                        "
                        class="research-source-card"
                    >
                        <div class="research-source-number">
                            {{ source.source_number }}
                        </div>

                        <div class="research-source-content">
                            <div class="research-source-meta">
                                <RouterLink
                                    :to="{
                                        name: 'document',
                                        params: {
                                            collectionId,
                                            documentId: source.document_id
                                        }
                                    }"
                                >
                                    {{ source.original_name }}
                                </RouterLink>

                                <span>
                                    фрагмент
                                    {{ source.chunk_index + 1 }}
                                </span>
                            </div>

                            <p>
                                {{ source.excerpt }}
                            </p>

                            <div class="research-score-row">
                                <span>
                                    Загальна:
                                    <strong>
                                        {{
                                            Number(
                                                source.score
                                            ).toFixed(3)
                                        }}
                                    </strong>
                                </span>

                                <span>
                                    Semantic:
                                    {{
                                        Number(
                                            source.semantic_score
                                        ).toFixed(3)
                                    }}
                                </span>

                                <span>
                                    Lexical:
                                    {{
                                        Number(
                                            source.lexical_score
                                        ).toFixed(3)
                                    }}
                                </span>
                            </div>
                        </div>
                    </article>
                </div>
            </div>

            <div
                v-else
                class="research-empty"
            >
                <h3>
                    Контекст не знайдено
                </h3>

                <p>
                    Спробуйте переформулювати запитання
                    або додайте більше опрацьованих документів.
                </p>
            </div>
        </template>
    </section>
</template>
