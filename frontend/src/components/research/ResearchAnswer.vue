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

const verified = computed(
    () => (
        props.generationMode === "local"
        && !props.result.fallback_used
        && !props.result.insufficient_evidence
        && props.result.grounded_claims?.length > 0
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
                                        ? "Безпечний fallback"
                                        : "Local LLM + auto-grounding"
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
                        title="Частка згенерованих тверджень, які KnowledgeHub зміг підтвердити знайденими джерелами."
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
                        title="Оцінка сили релевантних фрагментів, знайдених ще до запуску LLM."
                    >
                        Доказовість:
                        {{ evidencePercent }}%
                        ⓘ
                    </span>

                    <span
                        v-if="
                            result.response_language === 'uk'
                            && result.language_quality_passed
                        "
                        class="research-metric"
                        title="Українська відповідь пройшла обов'язковий редакторський етап і мовний контроль."
                    >
                        Український контроль ✓
                        ⓘ
                    </span>

                    <span
                        v-if="
                            result.language_rewrite_passes > 0
                        "
                    >
                        Редагувань:
                        {{ result.language_rewrite_passes }}
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
            Показано безпечну витягувальну відповідь.
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

        <ol
            v-else-if="result.answer_points?.length"
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

                <span
                    :title="
                        'Комбінована оцінка semantic similarity, lexical overlap та retrieval prior.'
                    "
                >
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
                !result.language_quality_passed
                && result.language_quality_issues?.length
            "
            class="research-language-audit"
        >
            <summary>
                Мовний контроль
            </summary>

            <ul>
                <li
                    v-for="issue in result.language_quality_issues"
                    :key="issue"
                >
                    {{ issue }}
                </li>
            </ul>
        </details>
    </div>
</template>
