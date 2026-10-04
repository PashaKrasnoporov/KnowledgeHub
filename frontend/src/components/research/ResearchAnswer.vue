<script setup>
import {
    computed,
    ref
} from "vue"

const props = defineProps({
    result: {
        type: Object,
        required: true
    },

    generationMode: {
        type: String,
        required: true
    }
})

defineEmits([
    "clear"
])

const copied = ref(false)

const groundingPercent = computed(
    () => Math.round(
        Number(
            props.result.grounding_coverage
            || 0
        )
        * 100
    )
)

const evidencePercent = computed(
    () => Math.round(
        Number(
            props.result.evidence_confidence
            || 0
        )
        * 100
    )
)

const languageScore = computed(
    () => Number(
        props.result.language_quality_score
        ?? 100
    )
)

const totalSeconds = computed(
    () => (
        Number(
            props.result.timings_ms?.total
            || 0
        ) / 1000
    ).toFixed(1)
)

const generationSeconds = computed(
    () => (
        Number(
            props.result.timings_ms?.llm_generation
            || 0
        ) / 1000
    ).toFixed(1)
)

const verified = computed(
    () => (
        props.generationMode === "local"
        && !props.result.fallback_used
        && !props.result.insufficient_evidence
        && props.result.grounded_claims?.length > 0
    )
)

const fallbackLabel = computed(
    () => (
        props.result.fallback_used
            ? "Перевірений витяг із джерел"
            : ""
    )
)

async function copyAnswer() {
    const text =
        props.result.generated_answer
        || ""

    if (!text) {
        return
    }

    try {
        await navigator.clipboard.writeText(
            text
        )

        copied.value = true

        window.setTimeout(
            () => {
                copied.value = false
            },
            1800
        )
    }
    catch {
        copied.value = false
    }
}
</script>

<template>
    <div class="research-answer">
        <div class="research-result-heading">
            <div>
                <div class="research-answer-title-row">
                    <h3>
                        {{
                            generationMode === "local"
                                ? "LLM-відповідь"
                                : "Чернетка відповіді"
                        }}
                    </h3>

                    <span
                        v-if="verified"
                        class="research-verified-badge"
                    >
                        ✓ Відповідь перевірена
                    </span>

                    <span
                        v-else-if="result.fallback_used"
                        class="research-source-fallback-badge"
                    >
                        {{ fallbackLabel }}
                    </span>
                </div>

                <div
                    v-if="result.generation_provider"
                    class="research-generation-meta"
                >
                    <span>
                        {{
                            result.insufficient_evidence
                                ? "Недостатньо доказів"
                                : (
                                    result.fallback_used
                                        ? "Source-extractive fallback"
                                        : "Fast local LLM + grounding"
                                )
                        }}
                    </span>

                    <span
                        v-if="result.generation_model"
                    >
                        {{ result.generation_model }}
                    </span>

                    <span
                        v-if="
                            !result.fallback_used
                            && result.grounded_claims?.length
                        "
                        class="research-metric"
                        title="Частка згенерованих тверджень, які підтверджені знайденими джерелами."
                    >
                        Покриття:
                        {{ groundingPercent }}%
                        ⓘ
                    </span>

                    <span
                        v-if="
                            result.evidence_confidence !== undefined
                            && generationMode === 'local'
                        "
                        class="research-metric"
                        title="Сила релевантних фрагментів, знайдених до запуску LLM."
                    >
                        Доказовість:
                        {{ evidencePercent }}%
                        ⓘ
                    </span>

                    <span
                        v-if="
                            result.response_language === 'uk'
                            && !result.fallback_used
                        "
                        class="research-metric"
                        title="М'яка інтегральна оцінка української мовної якості."
                    >
                        Українська:
                        {{ languageScore }}/100
                        ⓘ
                    </span>

                    <span
                        v-if="
                            result.language_rewrite_passes > 0
                            && !result.fallback_used
                        "
                    >
                        Rewrite:
                        {{ result.language_rewrite_passes }}
                    </span>
                </div>

                <div
                    v-if="result.timings_ms?.total"
                    class="research-performance-meta"
                >
                    <span
                        class="research-performance-chip"
                        title="Повний серверний час: retrieval + генерація + перевірки."
                    >
                        Загалом {{ totalSeconds }} с
                    </span>

                    <span
                        v-if="result.timings_ms?.llm_generation"
                        class="research-performance-chip"
                        title="Час безпосередньої генерації локальною LLM."
                    >
                        LLM {{ generationSeconds }} с
                    </span>

                    <span
                        v-if="result.timings_ms?.retrieval !== undefined"
                        class="research-performance-chip"
                        title="Час пошуку релевантних chunks."
                    >
                        Retrieval
                        {{ Math.round(result.timings_ms.retrieval) }} мс
                    </span>

                    <span
                        v-if="result.timings_ms?.claim_grounding !== undefined"
                        class="research-performance-chip"
                        title="Час перевірки тверджень і автоматичного підбору citations."
                    >
                        Grounding
                        {{ Math.round(result.timings_ms.claim_grounding) }} мс
                    </span>

                    <span
                        v-if="result.model_cold_start"
                        class="research-performance-chip is-warning"
                        title="Цей запит включав перше завантаження LLM після запуску backend."
                    >
                        Cold start
                    </span>
                </div>
            </div>

            <div class="research-answer-actions">
                <button
                    v-if="result.generated_answer"
                    class="research-clear-button"
                    type="button"
                    @click="copyAnswer"
                >
                    {{
                        copied
                            ? "Скопійовано"
                            : "Копіювати"
                    }}
                </button>

                <button
                    class="research-clear-button"
                    type="button"
                    @click="$emit('clear')"
                >
                    Очистити
                </button>
            </div>
        </div>

        <p
            v-if="
                result.fallback_used
                && result.generation_error
            "
            class="research-generation-warning"
        >
            {{ result.generation_error }}
            Нижче показано очищений витяг
            безпосередньо з першоджерел.
            Текст завантажених файлів не змінювався.
        </p>

        <p
            v-else-if="result.insufficient_evidence"
            class="research-generation-warning"
        >
            Система навмисно не запускає генерацію,
            коли знайдені докази недостатньо надійні.
        </p>

        <p
            v-else-if="
                !result.fallback_used
                && result.removed_claims > 0
            "
            class="research-grounding-note"
        >
            KnowledgeHub автоматично вилучив
            {{ result.removed_claims }}
            непідтверджене твердження
            з початкової LLM-відповіді.
        </p>

        <div
            v-if="
                !result.fallback_used
                && result.grounded_claims?.length
            "
            class="research-grounded-answer"
        >
            <p>
                <template
                    v-for="(
                        claim,
                        index
                    ) in result.grounded_claims"
                    :key="
                        `${index}-${claim.source_number}`
                    "
                >
                    <span>
                        {{ claim.text }}
                    </span>

                    <a
                        :href="
                            `#research-source-${claim.source_number}`
                        "
                        :title="
                            `Перейти до джерела ${claim.source_number}`
                        "
                    >
                        [{{ claim.source_number }}]
                    </a>

                    <span
                        v-if="
                            index
                            < result.grounded_claims.length - 1
                        "
                    >
                        &nbsp;
                    </span>
                </template>
            </p>
        </div>

        <div
            v-else-if="result.generated_answer"
            class="research-generated-answer"
        >
            {{ result.generated_answer }}
        </div>

        <details
            v-if="
                !result.fallback_used
                && result.grounded_claims?.length
            "
            class="research-claim-audit"
        >
            <summary>
                Перевірка тверджень
                ({{ result.grounded_claims.length }})
            </summary>

            <div
                v-for="(
                    claim,
                    index
                ) in result.grounded_claims"
                :key="
                    `${index}-${claim.source_number}`
                "
                class="research-claim-row"
            >
                <div>
                    <strong>
                        {{ index + 1 }}.
                    </strong>

                    {{ claim.text }}

                    <a
                        :href="
                            `#research-source-${claim.source_number}`
                        "
                    >
                        [{{ claim.source_number }}]
                    </a>
                </div>

                <span>
                    grounding
                    {{
                        Number(
                            claim.grounding_score
                        ).toFixed(3)
                    }}
                </span>
            </div>
        </details>

        <details
            v-if="
                result.language_quality_issues?.length
                || result.language_quality_warnings?.length
            "
            class="research-language-audit"
        >
            <summary>
                Мовний контроль
            </summary>

            <div
                v-if="result.language_quality_issues?.length"
                class="research-language-audit-group"
            >
                <strong>
                    Критичні зауваження
                </strong>

                <ul>
                    <li
                        v-for="issue in result.language_quality_issues"
                        :key="issue"
                    >
                        {{ issue }}
                    </li>
                </ul>
            </div>

            <div
                v-if="result.language_quality_warnings?.length"
                class="research-language-audit-group"
            >
                <strong>
                    Попередження
                </strong>

                <ul>
                    <li
                        v-for="warning in result.language_quality_warnings"
                        :key="warning"
                    >
                        {{ warning }}
                    </li>
                </ul>
            </div>
        </details>
    </div>
</template>
