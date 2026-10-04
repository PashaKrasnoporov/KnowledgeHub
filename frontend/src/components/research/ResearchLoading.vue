<script setup>
defineProps({
    elapsedSeconds: {
        type: Number,
        default: 0
    },

    localMode: {
        type: Boolean,
        default: false
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
                            ? "Формується LLM-відповідь"
                            : "Аналізуються документи"
                    }}
                </strong>

                <span>
                    {{
                        localMode
                            ? "Пошук доказів, генерація та перевірка тверджень."
                            : "Пошук релевантних фрагментів."
                    }}
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
            Це індикатор активного процесу,
            а не точний відсоток виконання.
        </p>
    </div>
</template>
