<script setup>
defineProps({
    errors: {
        type: Array,
        default: () => []
    },

    successMessage: {
        type: String,
        default: ""
    }
})
</script>

<template>
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

    <div
        v-if="successMessage"
        class="message message-success"
    >
        <p>
            {{ successMessage }}
        </p>
    </div>
</template>
