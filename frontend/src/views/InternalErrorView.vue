<script setup>
import {
    useAuth
} from "../composables/useAuth.js"

const {
    currentUser
} = useAuth()
</script>

<template>
    <section class="error-page">
        <div class="error-card">
            <div class="error-code">
                500
            </div>

            <p class="eyebrow">
                KNOWLEDGEHUB
            </p>

            <h1>
                Виникла внутрішня помилка
            </h1>

            <p class="error-description">
                Система не змогла виконати запит.
                Спробуйте повторити дію пізніше.
            </p>

            <div class="error-actions">
                <RouterLink
                    v-if="currentUser"
                    class="error-primary-button"
                    :to="{ name: 'collections' }"
                >
                    До колекцій
                </RouterLink>

                <RouterLink
                    class="error-secondary-button"
                    :to="{ name: 'home' }"
                >
                    На головну
                </RouterLink>
            </div>
        </div>
    </section>
</template>
