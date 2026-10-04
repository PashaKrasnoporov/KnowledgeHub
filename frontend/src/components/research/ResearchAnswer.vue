<script setup>
defineProps({
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
                                : "Local LLM"
                        }}
                    </span>

                    <span
                        v-if="result.generation_model"
                    >
                        {{ result.generation_model }}
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
            v-if="result.generation_error"
            class="research-generation-warning"
        >
            {{ result.generation_error }}
            Показано перевірену витягувальну відповідь.
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

        <p
            v-else
            class="research-empty-copy"
        >
            Релевантні фрагменти знайдено,
            але відповідь сформувати не вдалося.
            Перегляньте джерела нижче.
        </p>
    </div>
</template>
