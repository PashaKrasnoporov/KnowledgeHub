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
                404
            </div>

            <p class="eyebrow">
                KNOWLEDGEHUB
            </p>

            <h1>
                Сторінку не знайдено
            </h1>

            <p class="error-description">
                Можливо, адресу введено неправильно,
                сторінку було переміщено або видалено.
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
