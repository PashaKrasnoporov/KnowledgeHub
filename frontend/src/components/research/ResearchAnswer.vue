<script setup>
import {
    computed
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

const groundingPercent = computed(
    () => Math.round(
        Number(
            props.result.grounding_coverage
            || 0
        )
        * 100
    )
)
</script>

<template>
    <div class="research-answer">
        <div class="research-result-heading">
            <div>
                <h3>
                    {{
                        generationMode === "local"
                            ? "LLM-відповідь"
                            : "Чернетка відповіді"
                    }}
                </h3>

                <div
                    v-if="result.generation_provider"
                    class="research-generation-meta"
                >
                    <span>
                        {{
                            result.fallback_used
                                ? "Безпечний fallback"
                                : "Local LLM + auto-grounding"
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
                    >
                        Підтверджено:
                        {{ result.grounded_claims.length }}
                        твердж.
                    </span>

                    <span
                        v-if="
                            !result.fallback_used
                            && result.grounded_claims?.length
                        "
                    >
                        Покриття:
                        {{ groundingPercent }}%
                    </span>
                </div>
            </div>

            <button
                class="research-clear-button"
                type="button"
                @click="$emit('clear')"
            >
                Очистити
            </button>
        </div>

        <p
            v-if="
                result.fallback_used
                && result.generation_error
            "
            class="research-generation-warning"
        >
            {{ result.generation_error }}
            Показано перевірену витягувальну відповідь.
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
            v-if="result.generated_answer"
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

        <div
            v-if="
                !result.fallback_used
                && result.grounded_claims?.length
            "
            class="research-claim-audit"
        >
            <h4>
                Перевірка тверджень
            </h4>

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
        </div>

        <p
            v-if="
                !result.generated_answer
                && !result.answer_points?.length
            "
            class="research-empty-copy"
        >
            Релевантні фрагменти знайдено,
            але відповідь сформувати не вдалося.
            Перегляньте джерела нижче.
        </p>
    </div>
</template>
