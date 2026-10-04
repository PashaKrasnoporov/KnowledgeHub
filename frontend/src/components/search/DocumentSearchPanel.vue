<script setup>
import {
    computed
} from "vue"


const cloudLite = (
    import.meta.env.VITE_DEPLOYMENT_PROFILE
    === "railway-lite"
)

const props = defineProps({
    mode: {
        type: String,
        required: true
    },

    query: {
        type: String,
        required: true
    },

    searching: {
        type: Boolean,
        default: false
    },

    active: {
        type: Boolean,
        default: false
    },

    resultCount: {
        type: Number,
        default: 0
    }
})

const emit = defineEmits([
    "update:mode",
    "update:query",
    "search",
    "clear"
])

const modeHelp = computed(
    () => {
        if (cloudLite) {
            return (
                "Railway Lite використовує лексичний "
                + "пошук без важких ML-моделей."
            )
        }

        const descriptions = {
            lexical:
                "Lexical шукає точні збіги слів і фраз у текстах документів.",

            semantic:
                "Semantic шукає документи зі схожим змістом, навіть якщо слова запиту не збігаються буквально.",

            hybrid:
                "Hybrid поєднує пошук за словами та за змістом. Це основний рекомендований режим KnowledgeHub."
        }

        return descriptions[
            props.mode
        ] || ""
    }
)

const modeTitle = computed(
    () => (
        props.mode.charAt(0).toUpperCase()
        + props.mode.slice(1)
    )
)
</script>

<template>
    <section class="document-search">
        <div class="search-section-heading">
            <h2>
                Пошук у документах
            </h2>

            <p>
                Оберіть спосіб, яким система
                визначатиме релевантність документів.
            </p>
        </div>

        <form
            class="document-search-form"
            @submit.prevent="$emit('search')"
        >
            <div class="search-mode-field">
                <div class="label-with-info">
                    <label
                        class="document-search-label"
                        for="search-mode"
                    >
                        Режим
                    </label>

                    <span
                        class="info-tooltip"
                        tabindex="0"
                        aria-label="Інформація про режими пошуку"
                    >
                        <span class="info-icon">
                            i
                        </span>

                        <span class="tooltip-content">
                            <strong>
                                Режими пошуку
                            </strong>

                            <span>
                                <b>Lexical</b> — шукає
                                збіги конкретних слів
                                і фраз у тексті.
                            </span>

                            <span>
                                <b>Semantic</b> — шукає
                                документи зі схожим
                                змістом, навіть якщо
                                використані інші слова.
                            </span>

                            <span>
                                <b>Hybrid</b> — поєднує
                                пошук за словами
                                та пошук за змістом.
                            </span>
                        </span>
                    </span>
                </div>

                <select
                    id="search-mode"
                    class="search-mode-select"
                    :value="mode"
                    @change="
                        emit(
                            'update:mode',
                            $event.target.value
                        )
                    "
                >
                    <option
                        v-if="!cloudLite"
                        value="hybrid"
                    >
                        Hybrid
                    </option>

                    <option
                        v-if="!cloudLite"
                        value="semantic"
                    >
                        Semantic
                    </option>

                    <option value="lexical">
                        Lexical
                    </option>
                </select>
            </div>

            <div class="document-search-field">
                <label
                    class="document-search-label"
                    for="document-search-input"
                >
                    Запит
                </label>

                <input
                    id="document-search-input"
                    class="document-search-input"
                    type="search"
                    maxlength="200"
                    autocomplete="off"
                    placeholder="Наприклад: BM25, embeddings, RAG..."
                    :value="query"
                    @input="
                        emit(
                            'update:query',
                            $event.target.value
                        )
                    "
                >
            </div>

            <button
                class="document-search-button"
                type="submit"
                :disabled="searching"
            >
                {{
                    searching
                        ? "Пошук..."
                        : "Знайти"
                }}
            </button>
        </form>

        <div
            class="search-mode-help"
            aria-live="polite"
        >
            {{ modeHelp }}
        </div>

        <div
            v-if="active"
            class="search-summary"
        >
            <div>
                Знайдено:
                <strong>
                    {{ resultCount }}
                </strong>

                · режим:

                <strong>
                    {{ modeTitle }}
                </strong>

                · запит:

                <strong>
                    «{{ query }}»
                </strong>
            </div>

            <a
                href="#"
                @click.prevent="$emit('clear')"
            >
                Очистити пошук
            </a>
        </div>
    </section>
</template>
