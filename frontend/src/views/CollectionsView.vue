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

const searchQuery = ref("")
const activeQuery = ref("")
const sortValue = ref(
    "created_at-desc"
)

const name = ref("")
const description = ref("")

const modal = ref(null)
const nameInput = ref(null)
const submitting = ref(false)


function getSortParameters() {
    const [
        sortBy,
        sortOrder
    ] = sortValue.value.split("-")

    return {
        sortBy,
        sortOrder
    }
}


async function loadCollections() {
    loading.value = true
    errors.value = []

    const normalizedQuery =
        searchQuery.value.trim()

    const {
        sortBy,
        sortOrder
    } = getSortParameters()

    try {
        collections.value =
            await getCollections({
                q: normalizedQuery,
                sortBy,
                sortOrder
            })

        activeQuery.value =
            normalizedQuery
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


async function clearSearch() {
    searchQuery.value = ""

    await loadCollections()
}


function formatDate(value) {
    if (!value) {
        return ""
    }

    return new Intl.DateTimeFormat(
        "uk-UA",
        {
            year: "numeric",
            month: "2-digit",
            day: "2-digit"
        }
    ).format(
        new Date(value)
    )
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

        <section
            class="collections-toolbar"
            aria-label="Пошук і сортування колекцій"
        >
            <form
                class="collection-search-form"
                role="search"
                @submit.prevent="loadCollections"
            >
                <label
                    class="visually-hidden"
                    for="collection-search"
                >
                    Пошук колекцій
                </label>

                <input
                    id="collection-search"
                    v-model="searchQuery"
                    class="collection-search-input"
                    type="search"
                    maxlength="100"
                    autocomplete="off"
                    placeholder="Пошук за назвою або описом..."
                >

                <button
                    class="collection-search-button"
                    type="submit"
                    :disabled="loading"
                >
                    Знайти
                </button>

                <button
                    v-if="searchQuery || activeQuery"
                    class="collection-clear-button"
                    type="button"
                    :disabled="loading"
                    @click="clearSearch"
                >
                    Очистити
                </button>
            </form>

            <div class="collection-sort-control">
                <label for="collection-sort">
                    Сортування
                </label>

                <select
                    id="collection-sort"
                    v-model="sortValue"
                    :disabled="loading"
                    @change="loadCollections"
                >
                    <option value="created_at-desc">
                        Спочатку нові
                    </option>

                    <option value="created_at-asc">
                        Спочатку старі
                    </option>

                    <option value="updated_at-desc">
                        Нещодавно оновлені
                    </option>

                    <option value="name-asc">
                        Назва: А–Я
                    </option>

                    <option value="name-desc">
                        Назва: Я–А
                    </option>
                </select>
            </div>
        </section>

        <div
            v-if="!loading"
            class="collections-result-summary"
            aria-live="polite"
        >
            <span v-if="activeQuery">
                За запитом
                «{{ activeQuery }}»
                знайдено:
                {{ collections.length }}
            </span>

            <span v-else>
                Колекцій:
                {{ collections.length }}
            </span>
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
                                Створено:
                                {{ formatDate(collection.created_at) }}
                            </span>

                            <span class="collection-open">
                                Відкрити →
                            </span>
                        </div>
                    </article>
                </RouterLink>
            </div>

            <div
                v-else-if="activeQuery"
                class="empty-state"
            >
                <h2>
                    Колекцій не знайдено
                </h2>

                <p>
                    За запитом
                    «{{ activeQuery }}»
                    немає збігів у назвах
                    або описах колекцій.
                </p>

                <button
                    class="secondary-button"
                    type="button"
                    @click="clearSearch"
                >
                    Показати всі колекції
                </button>
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