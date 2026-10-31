<script setup>
import {
    ref,
    watch
} from "vue"

import {
    useAuth
} from "../../composables/useAuth.js"

import {
    isFavorite,
    toggleFavorite
} from "../../utils/favoriteItems.js"

const props = defineProps({
    collection: {
        type: Object,
        required: true
    }
})

defineEmits([
    "edit",
    "delete"
])

const {
    currentUser
} = useAuth()

const favorite =
    ref(false)

function syncFavorite() {
    if (
        !currentUser.value
        || !props.collection
    ) {
        favorite.value = false
        return
    }

    favorite.value =
        isFavorite(
            currentUser.value.id,
            {
                type: "collection",
                id:
                    props.collection.id,
                collectionId:
                    props.collection.id
            }
        )
}

function toggleCollectionFavorite() {
    if (!currentUser.value) {
        return
    }

    favorite.value =
        toggleFavorite(
            currentUser.value.id,
            {
                type: "collection",
                id:
                    props.collection.id,
                collectionId:
                    props.collection.id,
                name:
                    props.collection.name
            }
        )
}

watch(
    [
        currentUser,
        () => props.collection.id
    ],
    syncFavorite,
    {
        immediate: true
    }
)
</script>

<template>
    <div class="collection-detail-top">
        <div class="collection-detail-header">
            <p class="eyebrow">
                КОЛЕКЦІЯ
            </p>

            <h1>
                {{ collection.name }}
            </h1>

            <p v-if="collection.description">
                {{ collection.description }}
            </p>

            <p
                v-else
                class="collection-empty"
            >
                Опис не додано.
            </p>
        </div>

        <div class="collection-actions">
            <button
                class="secondary-button"
                type="button"
                :aria-pressed="favorite"
                @click="toggleCollectionFavorite"
            >
                {{
                    favorite
                        ? "★ В обраному"
                        : "☆ В обране"
                }}
            </button>

            <button
                class="secondary-button"
                type="button"
                @click="$emit('edit')"
            >
                Редагувати
            </button>

            <button
                class="danger-button"
                type="button"
                @click="$emit('delete')"
            >
                Видалити
            </button>
        </div>
    </div>
</template>
