<script setup>
defineProps({
    elapsedSeconds: {
        type: Number,
        default: 0
    },

    localMode: {
        type: Boolean,
        default: false
    },

    modelState: {
        type: String,
        default: "idle"
    }
})
</script>

<template>
    <div
        class="research-loading-status"
        role="status"
        aria-live="polite"
    >
        <div class="research-loading-heading">
            <span
                class="research-spinner"
                aria-hidden="true"
            ></span>

            <div>
                <strong>
                    {{
                        localMode
                            ? "Формується перевірена відповідь"
                            : "Аналізуються документи"
                    }}
                </strong>

                <span v-if="localMode && modelState === 'warming'">
                    Локальна модель ще готується у фоні.
                </span>

                <span v-else-if="localMode">
                    Швидкий pipeline: retrieval → generation → grounding.
                </span>

                <span v-else>
                    Виконується пошук релевантних фрагментів.
                </span>
            </div>

            <span class="research-elapsed">
                {{ elapsedSeconds }} с
            </span>
        </div>

        <div
            class="research-progress-track"
            aria-hidden="true"
        >
            <span
                class="research-progress-indicator"
            ></span>
        </div>

        <p>
            Показується реальний час очікування.
            Точний відсоток не імітується, оскільки
            backend поки не передає streaming-прогрес.
        </p>
    </div>
</template>
