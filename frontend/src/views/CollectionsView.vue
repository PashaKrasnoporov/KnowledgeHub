<script setup>
import {
    nextTick,
    onMounted,
    ref
} from "vue"

import {
    createCollection,
    getCollections
} from "../api/index.js"

const collections = ref([])
const loading = ref(true)
const errors = ref([])

const name = ref("")
const description = ref("")

const modal = ref(null)
const nameInput = ref(null)
const submitting = ref(false)

async function loadCollections() {
    loading.value = true
    errors.value = []

    try {
        collections.value =
            await getCollections()
    }
    catch (error) {
        errors.value = [
            error.message
        ]
    }
    finally {
        loading.value = false
    }
}

async function openModal() {
    modal.value?.showModal()

    await nextTick()

    nameInput.value?.focus()
}

function closeModal() {
    modal.value?.close()
}

function closeOnBackdrop(event) {
    if (
        event.target === modal.value
    ) {
        closeModal()
    }
}

async function submitCollection() {
    errors.value = []
    submitting.value = true

    try {
        await createCollection({
            name: name.value,
            description:
                description.value.trim() || null
        })

        name.value = ""
        description.value = ""

        closeModal()

        await loadCollections()
    }
    catch (error) {
        errors.value = [
            error.message
        ]
    }
    finally {
        submitting.value = false
    }
}

onMounted(
    loadCollections
)
</script>

<template>
    <section class="collections-page">
        <div class="collections-top">
            <div class="collections-header">
                <p class="eyebrow">
                    KNOWLEDGEHUB
                </p>

                <h1>
                    Мої колекції
                </h1>

                <p>
                    Організовуйте документи
                    в окремі тематичні колекції.
                </p>
            </div>

            <button
                class="new-collection-button"
                type="button"
                @click="openModal"
            >
                + Нова колекція
            </button>
        </div>

        <section class="collections-list">
            <div
                v-if="loading"
                class="empty-state"
            >
                <h2>
                    Завантаження...
                </h2>
            </div>

            <div
                v-else-if="collections.length"
                class="collections-grid"
            >
                <RouterLink
                    v-for="collection in collections"
                    :key="collection.id"
                    class="collection-card-link"
                    :to="{
                        name: 'collection-detail',
                        params: {
                            collectionId: collection.id
                        }
                    }"
                >
                    <article class="collection-card">
                        <div class="collection-card-top">
                            <div>
                                <p class="collection-label">
                                    КОЛЕКЦІЯ
                                </p>

                                <h2>
                                    {{ collection.name }}
                                </h2>
                            </div>
                        </div>

                        <p
                            v-if="collection.description"
                            class="collection-description"
                        >
                            {{ collection.description }}
                        </p>

                        <p
                            v-else
                            class="
                                collection-description
                                collection-empty
                            "
                        >
                            Опис не додано.
                        </p>

                        <div class="collection-card-footer">
                            <span>
                                ID: {{ collection.id }}
                            </span>

                            <span class="collection-open">
                                Відкрити →
                            </span>
                        </div>
                    </article>
                </RouterLink>
            </div>

            <div
                v-else
                class="empty-state"
            >
                <h2>
                    Колекцій поки немає
                </h2>

                <p>
                    Створіть першу колекцію,
                    щоб почати додавати документи.
                </p>

                <button
                    class="new-collection-button"
                    type="button"
                    @click="openModal"
                >
                    + Створити першу колекцію
                </button>
            </div>
        </section>

        <dialog
            ref="modal"
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
                            Нова колекція
                        </h2>
                    </div>

                    <button
                        class="modal-close-button"
                        type="button"
                        aria-label="Закрити"
                        @click="closeModal"
                    >
                        ×
                    </button>
                </div>

                <div
                    v-if="errors.length"
                    class="message message-error"
                >
                    <p
                        v-for="error in errors"
                        :key="error"
                    >
                        {{ error }}
                    </p>
                </div>

                <form
                    class="standard-form"
                    @submit.prevent="submitCollection"
                >
                    <div class="form-field">
                        <label for="collection-name">
                            Назва
                        </label>

                        <input
                            id="collection-name"
                            ref="nameInput"
                            v-model="name"
                            name="name"
                            type="text"
                            maxlength="100"
                            required
                            autocomplete="off"
                        >
                    </div>

                    <div class="form-field">
                        <label for="collection-description">
                            Опис
                        </label>

                        <textarea
                            id="collection-description"
                            v-model="description"
                            name="description"
                            maxlength="1000"
                            rows="5"
                        ></textarea>

                        <p class="form-hint">
                            Необов'язкове поле.
                        </p>
                    </div>

                    <div class="collection-modal-actions">
                        <button
                            class="secondary-button"
                            type="button"
                            @click="closeModal"
                        >
                            Скасувати
                        </button>

                        <button
                            class="form-submit"
                            type="submit"
                            :disabled="submitting"
                        >
                            {{
                                submitting
                                    ? "Створення..."
                                    : "Створити"
                            }}
                        </button>
                    </div>
                </form>
            </div>
        </dialog>
    </section>
</template>
