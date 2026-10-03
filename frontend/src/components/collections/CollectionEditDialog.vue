<script setup>
import {
    ref
} from "vue"

import {
    updateCollection
} from "../../api/index.js"

const props = defineProps({
    collection: {
        type: Object,
        required: true
    }
})

const emit = defineEmits([
    "saved",
    "error"
])

const dialog = ref(null)
const name = ref("")
const description = ref("")
const saving = ref(false)

function open() {
    name.value =
        props.collection?.name || ""

    description.value =
        props.collection?.description || ""

    dialog.value?.showModal()
}

function close() {
    dialog.value?.close()
}

function closeOnBackdrop(
    event
) {
    if (event.target === dialog.value) {
        close()
    }
}

async function submit() {
    saving.value = true

    try {
        const updated =
            await updateCollection(
                props.collection.id,
                {
                    name: name.value,
                    description:
                        description.value
                            .trim() || null
                }
            )

        close()

        emit(
            "saved",
            updated
        )
    }
    catch {
        emit(
            "error",
            "Перевірте назву та опис колекції."
        )
    }
    finally {
        saving.value = false
    }
}

defineExpose({
    open,
    close
})
</script>

<template>
    <dialog
        ref="dialog"
        class="collection-modal"
        @click="closeOnBackdrop"
    >
        <div class="collection-modal-content">
            <div class="collection-modal-header">
                <div>
                    <p class="eyebrow">
                        КОЛЕКЦІЯ
                    </p>

                    <h2>
                        Редагувати
                    </h2>
                </div>

                <button
                    class="modal-close-button"
                    type="button"
                    aria-label="Закрити"
                    @click="close"
                >
                    ×
                </button>
            </div>

            <form
                class="standard-form"
                @submit.prevent="submit"
            >
                <div class="form-field">
                    <label for="edit-collection-name">
                        Назва
                    </label>

                    <input
                        id="edit-collection-name"
                        v-model="name"
                        name="name"
                        type="text"
                        maxlength="100"
                        required
                    >
                </div>

                <div class="form-field">
                    <label for="edit-collection-description">
                        Опис
                    </label>

                    <textarea
                        id="edit-collection-description"
                        v-model="description"
                        name="description"
                        maxlength="1000"
                        rows="5"
                    ></textarea>
                </div>

                <div class="collection-modal-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        @click="close"
                    >
                        Скасувати
                    </button>

                    <button
                        class="form-submit"
                        type="submit"
                        :disabled="saving"
                    >
                        {{
                            saving
                                ? "Збереження..."
                                : "Зберегти"
                        }}
                    </button>
                </div>
            </form>
        </div>
    </dialog>
</template>
