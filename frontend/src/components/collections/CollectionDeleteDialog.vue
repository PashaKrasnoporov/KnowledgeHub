<script setup>
import {
    ref
} from "vue"

import {
    deleteCollection
} from "../../api/index.js"

const props = defineProps({
    collection: {
        type: Object,
        required: true
    }
})

const emit = defineEmits([
    "deleted",
    "error"
])

const dialog = ref(null)
const deleting = ref(false)

function open() {
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
    deleting.value = true

    try {
        await deleteCollection(
            props.collection.id
        )

        close()

        emit(
            "deleted"
        )
    }
    catch {
        close()

        emit(
            "error",
            "Не вдалося виконати операцію з колекцією."
        )
    }
    finally {
        deleting.value = false
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
        class="collection-modal delete-modal"
        @click="closeOnBackdrop"
    >
        <div class="collection-modal-content">
            <div class="collection-modal-header">
                <div>
                    <p class="eyebrow">
                        НЕБЕЗПЕЧНА ДІЯ
                    </p>

                    <h2>
                        Видалити колекцію?
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

            <div class="delete-warning">
                <p>
                    Колекція
                    <strong>
                        «{{ collection.name }}»
                    </strong>
                    буде видалена разом
                    з усіма її документами.
                </p>

                <p>
                    Цю дію неможливо скасувати.
                </p>
            </div>

            <form @submit.prevent="submit">
                <div class="collection-modal-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        @click="close"
                    >
                        Скасувати
                    </button>

                    <button
                        class="danger-button"
                        type="submit"
                        :disabled="deleting"
                    >
                        {{
                            deleting
                                ? "Видалення..."
                                : "Видалити назавжди"
                        }}
                    </button>
                </div>
            </form>
        </div>
    </dialog>
</template>
