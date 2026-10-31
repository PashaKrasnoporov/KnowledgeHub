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
const dragging = ref(false)
const uploadProgress = ref(0)

const MAX_SIZE =
    10 * 1024 * 1024

const ALLOWED = [
    ".pdf",
    ".docx",
    ".txt"
]


function reset() {
    selectedFile.value = null
    dragging.value = false
    uploadProgress.value = 0

    if (fileInput.value) {
        fileInput.value.value = ""
    }
}


function open() {
    reset()
    dialog.value?.showModal()
}


function close() {
    if (!uploading.value) {
        dialog.value?.close()
    }
}


function closeOnBackdrop(
    event
) {
    if (event.target === dialog.value) {
        close()
    }
}


function validate(
    file
) {
    if (!file) {
        return "Спочатку виберіть файл."
    }

    const name =
        file.name.toLowerCase()

    if (
        !ALLOWED.some(
            ext => name.endsWith(ext)
        )
    ) {
        return "Дозволені лише PDF, DOCX та TXT."
    }

    if (file.size > MAX_SIZE) {
        return "Файл перевищує максимально дозволений розмір 10 МБ."
    }

    return null
}


function setFile(
    file
) {
    const error =
        validate(file)

    if (error) {
        reset()

        emit(
            "error",
            error
        )

        return
    }

    selectedFile.value = file
    uploadProgress.value = 0
}


function selectFile(
    event
) {
    setFile(
        event.target.files?.[0]
        || null
    )
}


function chooseFile() {
    if (!uploading.value) {
        fileInput.value?.click()
    }
}


function dropFile(
    event
) {
    dragging.value = false

    if (!uploading.value) {
        setFile(
            event.dataTransfer?.files?.[0]
            || null
        )
    }
}


function fileSize(
    bytes
) {
    if (bytes < 1024 * 1024) {
        return `${
            (
                bytes / 1024
            ).toFixed(1)
        } КБ`
    }

    return `${
        (
            bytes
            / 1024
            / 1024
        ).toFixed(1)
    } МБ`
}


async function submit() {
    const error =
        validate(
            selectedFile.value
        )

    if (error) {
        emit(
            "error",
            error
        )

        return
    }

    uploading.value = true
    uploadProgress.value = 0

    try {
        await uploadDocument(
            props.collectionId,
            selectedFile.value,
            progress => {
                uploadProgress.value =
                    progress
            }
        )

        uploadProgress.value = 100

        dialog.value?.close()
        reset()

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
                error.message
                || "Не вдалося завантажити файл."
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
                    :disabled="uploading"
                    @click="close"
                >
                    ×
                </button>
            </div>

            <form
                class="standard-form"
                @submit.prevent="submit"
            >
                <input
                    ref="fileInput"
                    class="native-file-input"
                    type="file"
                    accept=".pdf,.docx,.txt"
                    :disabled="uploading"
                    @change="selectFile"
                >

                <div
                    class="drop-zone"
                    :class="{
                        dragging,
                        selected: selectedFile
                    }"
                    role="button"
                    tabindex="0"
                    @click="chooseFile"
                    @keydown.enter.prevent="chooseFile"
                    @keydown.space.prevent="chooseFile"
                    @dragenter.prevent="dragging = true"
                    @dragover.prevent="dragging = true"
                    @dragleave.prevent="dragging = false"
                    @drop.prevent="dropFile"
                >
                    <div class="drop-icon">
                        ↑
                    </div>

                    <template v-if="selectedFile">
                        <strong>
                            {{ selectedFile.name }}
                        </strong>

                        <span>
                            {{ fileSize(selectedFile.size) }}
                        </span>

                        <small v-if="!uploading">
                            Натисніть, щоб вибрати інший файл
                        </small>
                    </template>

                    <template v-else>
                        <strong>
                            Перетягніть файл сюди
                        </strong>

                        <span>
                            або натисніть, щоб вибрати
                        </span>

                        <small>
                            PDF, DOCX або TXT · до 10 МБ
                        </small>
                    </template>
                </div>

                <div
                    v-if="uploading"
                    class="upload-progress"
                >
                    <div class="upload-progress-header">
                        <span>
                            Завантаження файла
                        </span>

                        <strong>
                            {{ uploadProgress }}%
                        </strong>
                    </div>

                    <div
                        class="upload-progress-track"
                        role="progressbar"
                        :aria-valuenow="uploadProgress"
                        aria-valuemin="0"
                        aria-valuemax="100"
                    >
                        <div
                            class="upload-progress-bar"
                            :style="{
                                width: `${uploadProgress}%`
                            }"
                        ></div>
                    </div>
                </div>

                <div class="collection-modal-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        :disabled="uploading"
                        @click="close"
                    >
                        Скасувати
                    </button>

                    <button
                        class="form-submit"
                        type="submit"
                        :disabled="uploading || !selectedFile"
                    >
                        {{
                            uploading
                                ? `Завантаження ${uploadProgress}%`
                                : "Завантажити"
                        }}
                    </button>
                </div>
            </form>
        </div>
    </dialog>
</template>


<style scoped>
.native-file-input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

.drop-zone {
    display: flex;
    min-height: 210px;
    box-sizing: border-box;
    padding: 28px;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 8px;
    text-align: center;
    border: 2px dashed var(--mezha-temna);
    border-radius: 12px;
    background: var(--poverkhna);
    cursor: pointer;
    transition: 0.15s ease;
}

.drop-zone:hover,
.drop-zone:focus-visible,
.drop-zone.dragging {
    border-color: var(--blakytnyi-pryhlushenyi);
    background: var(--morska-pina);
    outline: none;
}

.drop-zone.dragging {
    transform: scale(1.01);
}

.drop-zone.selected {
    border-style: solid;
}

.drop-icon {
    display: flex;
    width: 46px;
    height: 46px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--blakytnyi-pryhlushenyi);
    color: var(--tekst-svitlyi);
    font-size: 24px;
    font-weight: 700;
}

.drop-zone strong {
    max-width: 100%;
    overflow-wrap: anywhere;
}

.drop-zone span,
.drop-zone small {
    color: var(--tekst-drugoryadnyi);
}

.upload-progress {
    display: grid;
    gap: 8px;
    margin-top: 18px;
}

.upload-progress-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    font-size: 14px;
}

.upload-progress-track {
    width: 100%;
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: var(--poverkhna);
    border: 1px solid var(--mezha);
}

.upload-progress-bar {
    height: 100%;
    border-radius: inherit;
    background: var(--blakytnyi-pryhlushenyi);
    transition: width 0.12s linear;
}

button:disabled {
    opacity: 0.55;
    cursor: default;
}
</style>
