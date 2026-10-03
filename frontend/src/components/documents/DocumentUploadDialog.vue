<script setup>
import {
    ref
} from "vue"

import {
    uploadDocument
} from "../../api/index.js"

const props = defineProps({
    collectionId: {
        type: Number,
        required: true
    }
})

const emit = defineEmits([
    "uploaded",
    "error"
])

const dialog = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)

function open() {
    selectedFile.value = null

    if (fileInput.value) {
        fileInput.value.value = ""
    }

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

function selectFile(
    event
) {
    selectedFile.value =
        event.target.files?.[0]
        || null
}

async function submit() {
    if (!selectedFile.value) {
        emit(
            "error",
            "Спочатку виберіть файл."
        )

        return
    }

    uploading.value = true

    try {
        await uploadDocument(
            props.collectionId,
            selectedFile.value
        )

        close()

        emit(
            "uploaded"
        )
    }
    catch (error) {
        if (error.status === 413) {
            emit(
                "error",
                "Файл перевищує максимально дозволений розмір 10 МБ."
            )
        }
        else if (error.status === 400) {
            emit(
                "error",
                "Некоректний файл. Дозволені PDF, DOCX та TXT."
            )
        }
        else {
            emit(
                "error",
                "Не вдалося завантажити файл."
            )
        }
    }
    finally {
        uploading.value = false
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
                        KNOWLEDGEHUB
                    </p>

                    <h2>
                        Додати документ
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
                    <label for="document-file">
                        Файл
                    </label>

                    <input
                        id="document-file"
                        ref="fileInput"
                        name="document_file"
                        type="file"
                        accept=".pdf,.docx,.txt"
                        required
                        @change="selectFile"
                    >

                    <p class="form-hint">
                        PDF, DOCX або TXT.
                        До 10 МБ.
                    </p>
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
                        :disabled="uploading"
                    >
                        {{
                            uploading
                                ? "Завантаження..."
                                : "Завантажити"
                        }}
                    </button>
                </div>
            </form>
        </div>
    </dialog>
</template>
