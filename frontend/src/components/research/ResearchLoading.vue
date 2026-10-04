<script setup>
import {
    computed
} from "vue"

const props = defineProps({
    elapsedSeconds: {
        type: Number,
        default: 0
    },

    localMode: {
        type: Boolean,
        default: false
    },

    ukrainianMode: {
        type: Boolean,
        default: false
    }
})

const phase = computed(
    () => {
        if (!props.localMode) {
            return "Пошук релевантних фрагментів"
        }

        if (props.elapsedSeconds < 4) {
            return "Пошук доказів у документах"
        }

        if (props.elapsedSeconds < 12) {
            return "Формування чернетки відповіді"
        }

        if (
            props.ukrainianMode
            && props.elapsedSeconds < 24
        ) {
            return "Українське мовне редагування"
        }

        return "Перевірка тверджень і джерел"
    }
)
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

                <span>
                    Орієнтовний етап:
                    {{ phase }}
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
            Смуга показує активний процес.
            Точний відсоток не відображається,
            поки backend не передає поетапний прогрес.
        </p>
    </div>
</template>
