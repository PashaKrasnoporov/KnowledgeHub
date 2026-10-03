<script setup>
defineProps({
    collection: {
        type: Object,
        required: true
    }
})

defineEmits([
    "edit",
    "delete"
])
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
