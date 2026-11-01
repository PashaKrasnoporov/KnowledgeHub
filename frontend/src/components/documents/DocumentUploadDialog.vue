<script setup>
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import { uploadDocument } from "../../api/index.js"

const props = defineProps({
    collectionId: { type: Number, required: true },
    existingDocuments: { type: Array, default: () => [] }
})

const emit = defineEmits(["uploaded", "opened"])
const router = useRouter()
const dialog = ref(null)
const fileInput = ref(null)
const items = ref([])
const dragging = ref(false)
const uploading = ref(false)
const batchMessage = ref("")
let nextItemId = 1

const MAX_SIZE = 10 * 1024 * 1024
const ALLOWED = [".pdf", ".docx", ".txt"]
const MAX_PARALLEL_UPLOADS = 1

const queuedCount = computed(() => items.value.filter(i => i.status === "queued").length)
const uploadingCount = computed(() => items.value.filter(i => i.status === "uploading").length)
const successCount = computed(() => items.value.filter(i => i.status === "success").length)
const duplicateCount = computed(() => items.value.filter(i => i.status === "duplicate").length)
const failedCount = computed(() => items.value.filter(i => i.status === "error" || i.status === "invalid").length)
const totalCount = computed(() => items.value.length)
const canUpload = computed(() => queuedCount.value > 0 && !uploading.value)

function reset() {
    items.value = []
    dragging.value = false
    uploading.value = false
    batchMessage.value = ""
    if (fileInput.value) fileInput.value.value = ""
}

function open() {
    reset()
    emit("opened")
    dialog.value?.showModal()
}

function close() {
    if (uploading.value) return
    dialog.value?.close()
    reset()
}

function closeOnBackdrop(event) {
    if (event.target === dialog.value) close()
}

function fileKey(file) {
    return [file.name, file.size, file.lastModified].join("::")
}

function normalizedName(value) {
    return String(value || "").trim().toLowerCase()
}

function validate(file) {
    const name = file.name.toLowerCase()
    if (!ALLOWED.some(ext => name.endsWith(ext))) {
        return "Формат не підтримується. Дозволені лише PDF, DOCX та TXT."
    }
    if (file.size > MAX_SIZE) {
        return "Файл перевищує максимально дозволений розмір 10 МБ."
    }
    return null
}

function addFiles(fileList) {
    if (!fileList || fileList.length === 0) return

    batchMessage.value = ""
    const existingKeys = new Set(items.value.map(item => item.key))
    const existingNames = new Set([
        ...props.existingDocuments.map(doc => normalizedName(doc.original_name)),
        ...items.value.map(item => normalizedName(item.name))
    ])

    let queueDuplicates = 0

    for (const file of Array.from(fileList)) {
        const key = fileKey(file)
        if (existingKeys.has(key)) {
            queueDuplicates += 1
            continue
        }

        existingKeys.add(key)
        const normalized = normalizedName(file.name)
        const nameConflict = existingNames.has(normalized)
        existingNames.add(normalized)

        const validationError = validate(file)

        items.value.push({
            id: nextItemId++,
            key,
            file,
            name: file.name,
            size: file.size,
            nameConflict,
            status: validationError ? "invalid" : "queued",
            progress: 0,
            error: validationError || "",
            existingDocumentId: null,
            existingDocumentName: ""
        })
    }

    if (queueDuplicates > 0) {
        batchMessage.value = queueDuplicates === 1
            ? "Цей локальний файл уже є у поточній черзі."
            : `${queueDuplicates} файлів уже є у поточній черзі.`
    }

    if (fileInput.value) fileInput.value.value = ""
}

function selectFiles(event) { addFiles(event.target.files) }

function chooseFiles() {
    if (uploading.value) return
    if (fileInput.value) fileInput.value.value = ""
    fileInput.value?.click()
}

function dropFiles(event) {
    dragging.value = false
    if (!uploading.value) addFiles(event.dataTransfer?.files)
}

function removeItem(itemId) {
    if (uploading.value) return
    items.value = items.value.filter(item => item.id !== itemId)
}

function clearList() {
    if (uploading.value) return
    items.value = []
    batchMessage.value = ""
}

function retryItem(item) {
    if (uploading.value || item.status !== "error") return
    item.status = "queued"
    item.progress = 0
    item.error = ""
    uploadQueued()
}

function openExisting(item) {
    if (!item.existingDocumentId) return
    dialog.value?.close()
    router.push({
        name: "document",
        params: {
            collectionId: props.collectionId,
            documentId: item.existingDocumentId
        }
    })
}

function fileSize(bytes) {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`
    return `${(bytes / 1024 / 1024).toFixed(1)} МБ`
}

function statusLabel(item) {
    return {
        queued: "Готовий до завантаження",
        uploading: `Завантаження ${item.progress}%`,
        success: "Завантажено",
        duplicate: "Уже існує",
        invalid: "Не можна додати",
        error: "Помилка завантаження"
    }[item.status] || item.status
}

function statusIcon(item) {
    if (item.status === "success") return "✓"
    if (item.status === "duplicate") return "="
    if (item.status === "error" || item.status === "invalid") return "!"
    return "↑"
}

function regularErrorMessage(error) {
    if (error?.status === 413) return "Файл перевищує максимально дозволений розмір 10 МБ."
    if (error?.status === 400) return "Файл не пройшов серверну перевірку. Переконайтеся, що це коректний PDF, DOCX або TXT."
    return error?.message || "Не вдалося завантажити файл."
}

async function uploadOne(item) {
    item.status = "uploading"
    item.progress = 0
    item.error = ""

    try {
        await uploadDocument(
            props.collectionId,
            item.file,
            progress => { item.progress = progress }
        )
        item.progress = 100
        item.status = "success"
    } catch (error) {
        item.progress = 0
        const detail = error?.detail

        if (error?.status === 409) {
            item.status = "duplicate"

            if (
                detail
                && typeof detail === "object"
            ) {
                item.existingDocumentId =
                    detail.existing_document_id
                    || null

                item.existingDocumentName =
                    detail.existing_document_name
                    || ""
            }

            item.error =
                item.existingDocumentName
                    ? `Такий самий вміст уже збережено як «${item.existingDocumentName}».`
                    : "Такий самий документ уже є в цій колекції."

            return
        }

        item.status = "error"
        item.error = regularErrorMessage(error)
    }
}

async function uploadQueued() {
    if (uploading.value || queuedCount.value === 0) return

    uploading.value = true
    batchMessage.value = ""
    const queue = items.value.filter(item => item.status === "queued")
    let cursor = 0

    async function worker() {
        while (cursor < queue.length) {
            const current = queue[cursor++]
            await uploadOne(current)
        }
    }

    const workerCount = Math.min(MAX_PARALLEL_UPLOADS, queue.length)
    await Promise.all(Array.from({ length: workerCount }, () => worker()))
    uploading.value = false

    const uploadedNow = queue.filter(item => item.status === "success").length
    const duplicateNow = queue.filter(item => item.status === "duplicate").length
    const failedNow = queue.filter(item => item.status === "error").length

    if (uploadedNow > 0) emit("uploaded", uploadedNow)

    const parts = []
    if (uploadedNow > 0) parts.push(`Завантажено: ${uploadedNow}`)
    if (duplicateNow > 0) parts.push(`Дублікатів пропущено: ${duplicateNow}`)
    if (failedNow > 0) parts.push(`Помилок: ${failedNow}`)
    if (parts.length) batchMessage.value = parts.join(" · ")
}

defineExpose({ open, close })
</script>

<template>
    <dialog
        ref="dialog"
        class="collection-modal batch-upload-modal"
        @click="closeOnBackdrop"
        @close="reset"
    >
        <div class="collection-modal-content batch-upload-content">
            <div class="collection-modal-header">
                <div>
                    <p class="eyebrow">KNOWLEDGEHUB</p>
                    <h2>Додати документи</h2>
                    <p class="batch-upload-description">
                        Можна вибрати одразу багато файлів. Однаковий вміст у межах цієї колекції повторно не зберігається.
                    </p>
                </div>
                <button
                    class="modal-close-button"
                    type="button"
                    aria-label="Закрити"
                    :disabled="uploading"
                    @click="close"
                >×</button>
            </div>

            <input
                ref="fileInput"
                class="native-file-input"
                type="file"
                multiple
                :disabled="uploading"
                aria-label="Вибрати документи"
                @change="selectFiles"
            >

            <div
                class="batch-drop-zone"
                :class="{ dragging }"
                role="button"
                tabindex="0"
                @click="chooseFiles"
                @keydown.enter.prevent="chooseFiles"
                @keydown.space.prevent="chooseFiles"
                @dragenter.prevent="dragging = true"
                @dragover.prevent="dragging = true"
                @dragleave.prevent="dragging = false"
                @drop.prevent="dropFiles"
            >
                <div class="batch-drop-icon">↑</div>
                <div>
                    <strong>Перетягніть файли сюди</strong>
                    <span>або натисніть, щоб вибрати один чи кілька документів</span>
                    <small>PDF, DOCX або TXT · до 10 МБ кожен</small>
                </div>
            </div>

            <div v-if="totalCount" class="batch-summary" aria-live="polite">
                <span>У списку: <strong>{{ totalCount }}</strong></span>
                <span v-if="queuedCount">Очікує: <strong>{{ queuedCount }}</strong></span>
                <span v-if="uploadingCount">Завантажується: <strong>{{ uploadingCount }}</strong></span>
                <span v-if="successCount">Завантажено: <strong>{{ successCount }}</strong></span>
                <span v-if="duplicateCount" class="batch-summary-duplicate">
                    Дублікати: <strong>{{ duplicateCount }}</strong>
                </span>
                <span v-if="failedCount" class="batch-summary-error">
                    Помилки: <strong>{{ failedCount }}</strong>
                </span>
            </div>

            <div v-if="batchMessage" class="batch-message" role="status">
                {{ batchMessage }}
            </div>

            <section v-if="items.length" class="upload-file-list" aria-label="Файли для завантаження">
                <article
                    v-for="item in items"
                    :key="item.id"
                    class="upload-file-item"
                    :class="[`status-${item.status}`]"
                >
                    <div class="upload-file-icon">{{ statusIcon(item) }}</div>

                    <div class="upload-file-main">
                        <strong class="upload-file-name" :title="item.name">{{ item.name }}</strong>

                        <div class="upload-file-meta">
                            <span>{{ fileSize(item.size) }}</span>
                            <span>{{ statusLabel(item) }}</span>
                        </div>

                        <p
                            v-if="item.nameConflict && (item.status === 'queued' || item.status === 'uploading')"
                            class="upload-file-warning"
                        >
                            У колекції або черзі вже є файл з такою назвою. Вміст буде перевірено окремо.
                        </p>

                        <div v-if="item.status === 'uploading'" class="upload-item-progress">
                            <div :style="{ width: `${item.progress}%` }"></div>
                        </div>

                        <p v-if="item.error" class="upload-file-error">{{ item.error }}</p>
                    </div>

                    <div class="upload-file-actions">
                        <button
                            v-if="item.status === 'duplicate' && item.existingDocumentId"
                            type="button"
                            class="upload-item-action"
                            @click="openExisting(item)"
                        >
                            Відкрити існуючий
                        </button>

                        <button
                            v-if="item.status === 'error'"
                            type="button"
                            class="upload-item-action"
                            :disabled="uploading"
                            @click="retryItem(item)"
                        >
                            Повторити
                        </button>

                        <button
                            v-if="item.status !== 'uploading'"
                            type="button"
                            class="upload-item-remove"
                            :disabled="uploading"
                            :aria-label="`Прибрати ${item.name} зі списку`"
                            title="Прибрати зі списку"
                            @click="removeItem(item.id)"
                        >×</button>
                    </div>
                </article>
            </section>

            <div class="batch-upload-footer">
                <div class="batch-secondary-actions">
                    <button class="secondary-button" type="button" :disabled="uploading" @click="close">Закрити</button>
                    <button class="secondary-button" type="button" :disabled="uploading" @click="chooseFiles">+ Додати ще</button>
                    <button
                        v-if="items.length"
                        class="batch-clear-button"
                        type="button"
                        :disabled="uploading"
                        @click="clearList"
                    >Очистити список</button>
                </div>

                <button
                    class="form-submit batch-upload-submit"
                    type="button"
                    :disabled="!canUpload"
                    @click="uploadQueued"
                >
                    {{
                        uploading
                            ? "Завантаження..."
                            : (queuedCount === 1 ? "Завантажити 1 файл" : `Завантажити ${queuedCount} файлів`)
                    }}
                </button>
            </div>
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

.collection-modal.batch-upload-modal {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    right: auto !important;
    bottom: auto !important;
    transform: translate(-50%, -50%) !important;
    width: min(780px, calc(100vw - 32px)) !important;
    max-width: calc(100vw - 32px) !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: calc(100dvh - 32px) !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.batch-upload-content {
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: calc(100dvh - 34px) !important;
    padding: 28px !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}

.batch-upload-description {
    max-width: 610px;
    margin: 7px 0 0;
    color: var(--tekst-drugoryadnyi);
    font-size: 13px;
    line-height: 1.5;
}

.batch-drop-zone {
    display: flex;
    width: 100%;
    min-width: 0;
    min-height: 118px;
    flex: 0 0 auto;
    align-items: center;
    gap: 16px;
    padding: 18px 20px;
    box-sizing: border-box;
    border: 2px dashed var(--mezha-temna);
    border-radius: 12px;
    background: var(--poverkhna);
    cursor: pointer;
}

.batch-drop-zone:hover,
.batch-drop-zone:focus-visible,
.batch-drop-zone.dragging {
    border-color: var(--blakytnyi-pryhlushenyi);
    background: var(--morska-pina);
    outline: none;
}

.batch-drop-icon {
    display: flex;
    width: 48px;
    height: 48px;
    flex: 0 0 48px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--blakytnyi-pryhlushenyi);
    color: var(--tekst-svitlyi);
    font-size: 23px;
    font-weight: 700;
}

.batch-drop-zone > div:last-child {
    display: grid;
    gap: 4px;
    min-width: 0;
}

.batch-drop-zone span,
.batch-drop-zone small {
    color: var(--tekst-drugoryadnyi);
}

.batch-drop-zone small {
    font-size: 12px;
}

.batch-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    margin-top: 14px;
    padding: 10px 12px;
    border: 1px solid var(--mezha);
    border-radius: 9px;
    background: var(--poverkhna-svitla);
    color: var(--tekst-drugoryadnyi);
    font-size: 12px;
}

.batch-summary strong {
    color: var(--morskyi-hlybokyi);
}

.batch-summary-duplicate,
.batch-summary-duplicate strong {
    color: var(--akvamarin-temnyi);
}

.batch-summary-error,
.batch-summary-error strong {
    color: var(--pomylka-tekst);
}

.batch-message {
    margin-top: 10px;
    padding: 10px 12px;
    border: 1px solid var(--mezha);
    border-radius: 8px;
    background: var(--poverkhna);
    color: var(--tekst-drugoryadnyi);
    font-size: 13px;
}

.upload-file-list {
    display: grid;
    flex: 0 1 auto;
    gap: 8px;
    min-height: 0;
    max-height: min(360px, 42dvh);
    margin-top: 14px;
    padding-right: 6px;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-gutter: stable;
}

.upload-file-item {
    display: grid;
    width: 100%;
    min-width: 0;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: start;
    gap: 12px;
    padding: 12px 13px;
    box-sizing: border-box;
    border: 1px solid var(--mezha);
    border-radius: 10px;
    background: var(--poverkhna-svitla);
}

.upload-file-item.status-success {
    border-color: var(--uspikh-mezha);
    background: var(--uspikh-fon);
}

.upload-file-item.status-duplicate {
    border-color: var(--mezha-temna);
    background: var(--morska-pina);
}

.upload-file-item.status-error,
.upload-file-item.status-invalid {
    border-color: var(--pomylka-mezha);
    background: var(--pomylka-fon);
}

.upload-file-icon {
    display: flex;
    width: 30px;
    height: 30px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--morska-pina);
    color: var(--morskyi-hlybokyi);
    font-size: 13px;
    font-weight: 800;
}

.status-success .upload-file-icon {
    background: var(--uspikh-mezha);
    color: #ffffff;
}

.status-duplicate .upload-file-icon {
    background: var(--blakytnyi-pryhlushenyi);
    color: #ffffff;
}

.status-error .upload-file-icon,
.status-invalid .upload-file-icon {
    background: var(--pomylka-mezha);
    color: #ffffff;
}

.upload-file-main {
    min-width: 0;
}

.upload-file-name {
    display: block;
    max-width: 100%;
    overflow: hidden;
    color: var(--tekst-osnovnyi);
    font-size: 13px;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.upload-file-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 10px;
    margin-top: 4px;
    color: var(--tekst-drugoryadnyi);
    font-size: 11px;
}

.upload-file-warning {
    margin: 6px 0 0;
    color: var(--akvamarin-temnyi);
    font-size: 12px;
    line-height: 1.4;
}

.upload-file-error {
    margin: 6px 0 0;
    color: var(--pomylka-tekst);
    font-size: 12px;
    line-height: 1.4;
}

.status-duplicate .upload-file-error {
    color: var(--akvamarin-temnyi);
}

.upload-item-progress {
    height: 6px;
    margin-top: 8px;
    overflow: hidden;
    border-radius: 999px;
    background: var(--poverkhna);
}

.upload-item-progress > div {
    height: 100%;
    border-radius: inherit;
    background: var(--blakytnyi-pryhlushenyi);
}

.upload-file-actions {
    display: flex;
    align-items: center;
    gap: 6px;
}

.upload-item-action,
.upload-item-remove,
.batch-clear-button {
    border: 1px solid var(--mezha-temna);
    background: var(--poverkhna-svitla);
    color: var(--akvamarin-temnyi);
    font: inherit;
    cursor: pointer;
}

.upload-item-action {
    min-height: 32px;
    padding: 0 10px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 700;
}

.upload-item-remove {
    display: inline-flex;
    width: 32px;
    height: 32px;
    align-items: center;
    justify-content: center;
    padding: 0;
    border-radius: 50%;
    font-size: 18px;
}

.batch-upload-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--mezha);
}

.batch-secondary-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.batch-clear-button {
    min-height: 40px;
    padding: 0 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
}

.batch-upload-submit {
    flex-shrink: 0;
    min-width: 160px;
}

button:disabled {
    opacity: 0.55;
    cursor: default;
}

@media (max-width: 700px) {
    .collection-modal.batch-upload-modal {
        width: calc(100vw - 16px) !important;
        max-width: calc(100vw - 16px) !important;
        max-height: calc(100dvh - 16px) !important;
    }

    .batch-upload-content {
        max-height: calc(100dvh - 18px) !important;
        padding: 18px !important;
    }

    .batch-drop-zone {
        align-items: flex-start;
    }

    .upload-file-item {
        grid-template-columns: auto minmax(0, 1fr);
    }

    .upload-file-actions {
        grid-column: 2;
    }

    .batch-upload-footer {
        align-items: stretch;
        flex-direction: column;
    }

    .batch-secondary-actions {
        width: 100%;
    }

    .batch-upload-submit {
        width: 100%;
    }
}
</style>
